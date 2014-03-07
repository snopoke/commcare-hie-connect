# -*- coding: utf-8 -*-
import hie
import unittest
from hie_connect.commcare_hq_client import MockCommCareHqClient


class HieForwarderTestCase(unittest.TestCase):
    """
    This is not a real test but just a way of faking a post
    """

    def setUp(self):
        """Before each test, set up a blank database"""
        hie.app.config['TESTING'] = True
        hie.hq_client._hq_api_client = MockCommCareHqClient({
            'user': [
                (
                    '655a8581da22f05fb953b19d8561b079',
                    {
                        'user_id': '655a8581da22f05fb953b19d8561b079',
                        'first_name': 'jack',
                        'last_name': 'winkler',
                        'default_phone_number': '+275552346867',
                        'user_data': {
                            'hwc_code': 'hwc_123'
                        }
                    }
                )
            ]
        })
        self.app = hie.app.test_client()

    def test_post(self):
        data = """
        <case case_id="12429aad-d209-4987-a4cc-9f0f0d33189c"
        date_modified="2013-09-18T12:59:18Z" user_id="655a8581da22f05fb953b19d8561b079"
        xmlns="http://commcarehq.org/case/transaction/v2">
            <create>
                <case_type>mother</case_type>
                <case_name>123456</case_name>
                <owner_id>655a8581da22f05fb953b19d8561b079</owner_id>
            </create>
            <update>
                <pregnancy_status>confirmed</pregnancy_status>
                <pregnancy_date>2014-09-02</pregnancy_date>
                <id>123456789090</id>
                <id_type>NI</id_type>
                <id_authority>ZAF</id_authority>
                <dob>1977-09-02</dob>
                <given_name>Jane</given_name>
                <family_name>Doe</family_name>
                <forward_to_hie>1</forward_to_hie>
                <mobile_number>+275556784445</mobile_number>
                <lang_code>eng</lang_code>
                <facility_id>1</facility_id>
                <facility_name>Clinic 1</facility_name>
                <pregnancy_date_type>lmp</pregnancy_date_type>
            </update>
        </case>"""
        rv = self.app.post('/forward/', data=data, follow_redirects=True)

if __name__ == '__main__':
    unittest.main()