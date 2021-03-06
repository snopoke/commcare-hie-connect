from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import hashlib
import logging
import json
import traceback
import uuid
import os
from datetime import datetime
from StringIO import StringIO
from xml.etree import ElementTree as ET

import requests
from flask import Flask, request, redirect, url_for, Response, render_template
from requests.auth import HTTPBasicAuth

from hie_connect.commcare_hq_client import CommCareHqClient, AUTH_MODE_DIGEST
import hie_connect.const as const


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('hie')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

from hie_connect.models import Record, db
db.init_app(app)


def save_error(record):
    f = StringIO()
    traceback.print_exc(file=f)
    record.error = f.getvalue()
    return save_record(record)


def save_record(record):
    try:
        db.session.add(record)
        db.session.commit()
    except:
        logger.exception("Error saving record to DB")

    return Response(status=200)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/records.json')
def records():
    user_id = request.args.get('user', None)
    case_id = request.args.get('case', None)

    query = Record.query.order_by(Record.date.desc())
    if user_id:
        query = query.filter(Record.user_id == user_id)
    if case_id:
        query = query.filter(Record.case_id == case_id)

    page = int(request.args.get('page', 0))
    limit = int(request.args.get('limit', 5))
    start = limit*page
    end = start+limit
    rs = [r.to_dict() for r in query[start:end]]
    return json.dumps({
        'total': Record.query.count(),
        'page': page,
        'limit': limit,
        'records': rs,
    })


@app.route('/forward/', methods=['POST'])
def forward_data():
    if request.method == 'POST':
        if not request.data:
            app.logger.warn('No data in post')

        record = Record()
        record.case = request.data
        try:
            root = ET.fromstring(request.data)
            record.case_id = root.attrib.get(const.ATTR_CASE_ID)
            record.user_id = root.attrib.get(const.ATTR_USER_ID)
            record.name = '{} {}'.format(
                get_case_property(root, const.GIVEN_NAME),
                get_case_property(root, const.FAMILY_NAME)
            )
            case, msg = parse_case(root)
        except:
            return save_error(record)

        if not case:
            record.error = msg
            return save_record(record)
        else:
            try:
                mhd, cda = get_mhd_cda(case)
            except:
                return save_error(record)

            record.mhd = json.dumps(mhd, sort_keys=True, indent=4)
            record.cda = cda

            try:
                code, text = post(app.config['HIE_REGISTER_URL'], mhd, cda)
                record.response_code = code
                record.response_text = text
                return save_record(record)
            except:
                return save_error(record)
    else:
        return redirect(url_for('index'))


def parse_case(root):
    try:
        forward = get_case_property(root, const.FORWARD_TO_HIE)
        if forward != '1':
            return None, 'Ignoring case - not flagged for forwarding'

        status = get_case_property(root, const.PREGNANCY_STATUS)
        if not status:
            return None, 'No pregnancy status'

        if status in const.STATUS_LIST:
            opened_on = root.attrib[const.ATTR_LAST_MODIFIED]
            opened_on = reformat_date(opened_on, '%Y-%m-%dT%H:%M:%SZ', const.DATE_FORMAT_SHORT)
            pregnancy_date = get_case_property(root, const.PREGNANCY_DATE)
            pregnancy_date = reformat_date(pregnancy_date, '%Y-%m-%d', const.DATE_FORMAT_SHORT)
            dob = get_case_property(root, const.DOB)
            dob = reformat_date(dob, '%Y-%m-%d', const.DATE_FORMAT_SHORT)

            id_dict = dict(
                id_num=get_case_property(root, const.ID_NUMBER),
                id_authority=get_case_property(root, const.ID_AUTHORITY),
                id_type=get_case_property(root, const.ID_TYPE),
            )

            user_id = root.attrib.get(const.ATTR_USER_ID)
            user = get_user(user_id)
            case_data = dict(
                uniqueId=generate_oid(),
                createdTime=datetime.now().strftime(const.DATE_FORMAT_LONG),
                pidCX="{id_num}^^^{id_authority}^{id_type}".format(**id_dict),
                cellNumber=get_case_property(root, const.MOBILE_NUMBER),
                givenName=get_case_property(root, const.GIVEN_NAME),
                familyName=get_case_property(root, const.FAMILY_NAME),
                birthDate=dob,
                languageCode=get_case_property(root, const.LANG_CODE),
                authoredTime=opened_on,
                hcwCode=user['user_data']['hwc_code'],
                hcwCellNumber=user['default_phone_number'],
                hcwGivenName=user['first_name'],
                hcwFamilyName=user['last_name'],
                facilityId=get_case_property(root, const.FACILITY_ID),
                facilityName=get_case_property(root, const.FACILITY_NAME),
                encounterDateTime=opened_on,
                effectiveTime=datetime.now().strftime(const.DATE_FORMAT_LONG),
                status=status,
                date_type=get_case_property(root, const.PREGNANCY_DATE_TYPE),
                date=pregnancy_date,
            )

            for k, v in case_data.items():
                if v is None:
                    return None, 'Field missing from case: %s' % k

            return case_data, None
        else:
            return None, 'Ignoring case with status %s' % status
    except AttributeError:
        app.logger.exception('Error processing case')
        raise


def get_case_property(case_root, xpath):
    node = case_root.find(xpath)
    if node is not None:
        return node.text

    logger.debug('case property not found %s', xpath)
    return None


def reformat_date(date_string, current_format, new_format):
    if date_string:
        return datetime.strptime(date_string, current_format).strftime(new_format)


def post(url, mhd, cda):
    response = requests.post(
        '%s%s' % (app.config['HIE_URL_BASE'], url),
        files={
            "ihe-mhd-metadata": ("MHDMetadata.json", StringIO(json.dumps(mhd))),
            "content": ("CDARequest.xml", StringIO(cda))
        },
        verify=False,
        auth=HTTPBasicAuth(app.config['HIE_USERNAME'], app.config['HIE_PASSWORD'])
    )
    return response.status_code, response.text


def generate_oid():
    id = uuid.uuid1().__str__()
    hex = id.replace("-", "")
    dec = int(hex, 16)
    return "2.25." + str(dec)


def get_user(user_id):
    # API's don't include which project the data comes form so have to statically define for now
    project = app.config['COMMCAREHQ_PROJECT']
    return hq_client().get('user', id=user_id, project=project)


def get_mhd_cda(context):
    cda = render_template('cda.html', **context)
    mhd = const.MHD_BASE.copy()
    entry = mhd['documentEntry']
    entry['patientId'] = context['pidCX']
    entry['uniqueId'] = context['uniqueId']
    entry['entryUUID'] = 'urn:uuid:{}'.format(uuid.uuid1())
    entry['hash'] = hashlib.sha1(cda.encode()).hexdigest()
    entry['size'] = len(cda)
    return mhd, cda


def hq_client():
    if not hasattr(hq_client, '_hq_api_client'):
        hq_client._hq_api_client = CommCareHqClient(
            app.config['COMMCARE_API_ROOT'],
            None
        ).authenticated(app.config['COMMCARE_API_USER'], app.config['COMMCARE_API_PASSWORD'], AUTH_MODE_DIGEST)
    return hq_client._hq_api_client


if __name__ == '__main__':
    app.run()
