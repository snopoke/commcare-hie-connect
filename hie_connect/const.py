DATE_FORMAT_SHORT = "%Y%m%d"
DATE_FORMAT_LONG = '%Y%m%d%H%M%S'

xmlns_prefix = './/{http://commcarehq.org/case/transaction/v2}'


class P(str):
    @property
    def p(self):
        return ('{}' + self).format(xmlns_prefix)


ATTR_USER_ID = 'user_id'
ATTR_CASE_ID = 'case_id'
ATTR_LAST_MODIFIED = 'date_modified'

DOMAIN = P('domain').p
FORWARD_TO_HIE = P('forward_to_hie').p
GIVEN_NAME = P('given_name').p
PREGNANCY_STATUS = P('pregnancy_status').p
ID_NUMBER = P('id_number').p
ID_AUTHORITY = P('id_authority').p
ID_TYPE = P('id_type').p
FAMILY_NAME = P('family_name').p
DOB = P('dob').p
PREGNANCY_DATE_TYPE = P('pregnancy_date_type').p
FACILITY_NAME = P('facility_name').p
FACILITY_ID = P('facility_id').p
LANG_CODE = P('lang_code').p
MOBILE_NUMBER = P('mobile_number').p
PREGNANCY_DATE = P('pregnancy_date').p

STATUS_LIST = [
    'suspected',
    'confirmed',
    'delivered'
]

DATE_TYPES = [
    'edd',
    'lmp',
    'dob'
]

MHD_BASE = {
    "documentEntry": {
        "classCode": {"code": "51855-5", "codingScheme": "2.16.840.1.113883.6.1", "codeName": "Patient Note"},
        "typeCode": {"code": "51855-5", "codingScheme": "2.16.840.1.113883.6.1", "codeName": "Patient Note"},
        "formatCode": {"code": "npr-pn-cda", "codingScheme": "4308822c-d4de-49db-9bb8-275394ee971d",
                       "codeName": "NPR Patient Note CDA"},
        "mimeType": "text/xml",
    }
}