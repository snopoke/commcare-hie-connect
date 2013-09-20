import logging
import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, Response, render_template
from xml.etree import ElementTree as ET
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('hie')
logger.setLevel(logging.DEBUG)

USERNAME = 'test'
PASSWORD = 'test'

HIE_URL = 'https://test.jembi.org:5000'
HIE_REGISTER_ULR = '/ws/rest/v1/patients/'
HIE_ENCOUNTER_URL = '/ws/rest/v1/patient/NID-{}/encounters'

xmlns_prefix = './/{http://commcarehq.org/case/transaction/v2}'
FORWARD_TO_HIE = '{}forward_to_hie'.format(xmlns_prefix)
GIVEN_NAME = '{}given_name'.format(xmlns_prefix)
PREGNANCY_STATUS = '{}pregnancy_status'.format(xmlns_prefix)
ID_NUMBER = '{}nid'.format(xmlns_prefix)
GENDER = '{}gender'.format(xmlns_prefix)
FAMILY_NAME = '{}family_name'.format(xmlns_prefix)
DOB = '{}dob'.format(xmlns_prefix)

STATUS_MAP = {
    'suspected': ('Pregnancy, not (yet) confirmed', 'Z32.0'),
    'confirmed': ('Pregnancy, confirmed', 'Z32.9')
}

GENDER_MAP = {
    'male': 'M',
    'female': 'F',
}

app = Flask(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('HIE_SETTINGS', silent=True)


@app.route('/')
def index():
    return 'OpenHIE data forwarder.'


@app.route('/forward/', methods=['POST'])
def forward_data():
    if request.method == 'POST':
        print request.data

        if not request.data:
            app.logger.warn('No data in post')

        case = parse_case(request.data)
        if case:
            print send_registration(case)
            print send_encounter(case)

        return Response(status=200)
    else:
        return redirect(url_for('index'))


def parse_case(data):
    try:
        root = ET.fromstring(data)
        forward = get_case_property(FORWARD_TO_HIE)
        if forward != 1:
            logger.debug('Ignoring case - not flagged for forwarding')
            return None

        status = get_case_property(PREGNANCY_STATUS)
        if not status:
            logger.info('No pregnancy status')
            return None

        if status in ['suspected', 'confirmed']:
            dob = get_case_property(root, DOB)
            dob = reformat_date(dob, '%Y-%m-%d', '%Y%m%d')
            now = root.attrib.get('date_modified')
            now = reformat_date(now, '%Y-%m-%dT%H:%M:%SZ', '%Y%m%d%H%M%S')

            gender = get_case_property(root, GENDER)
            if gender and len(gender) == 1:
                gender = gender.upper()
            elif gender:
                gender = GENDER_MAP.get(gender.lower())

            case_data = dict(
                now=now,
                dob=dob,
                given_name=get_case_property(root, GIVEN_NAME),
                family_name=get_case_property(root, FAMILY_NAME),
                gender=gender,
                nid=get_case_property(root, ID_NUMBER),
                obs_status=STATUS_MAP[status][0],
                obs_code=STATUS_MAP[status][1],
            )

            for k, v in case_data:
                if v is None:
                    logger.error('Field missing from case: %s', k)
                    return None

            return case_data
        else:
            logger.info('Ignoring case with status %s' % status)
    except AttributeError as e:
        app.logger.exception('Error processing case')
        return None


def get_case_property(case_root, xpath):
    node = case_root.find(xpath)
    if node is not None:
        return node.text

    logger.debug('case property not found %s', xpath)
    return None


def reformat_date(date_string, current_format, new_format):
    if date_string:
        return datetime.strptime(date_string, current_format).strftime(new_format)


def send_registration(case):
    body = render_template('register.html', **case)
    return post(HIE_REGISTER_ULR, body)


def send_encounter(case):
    body = render_template('encounter.html', **case)
    url = HIE_ENCOUNTER_URL.format(case['nid'])
    return post(url, body)


def post(url, data):
    response = requests.post('%s%s' % (HIE_URL, url), data=data, verify=False, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return response.status_code, response.text


if __name__ == '__main__':
    app.run()
