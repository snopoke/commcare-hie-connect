# -*- coding: utf-8 -*-
import os
import hie
import unittest
import tempfile


class HieForwarderTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database"""
        hie.app.config['TESTING'] = True
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
                <dob>1977-09-02</dob>
                <given_name>Jane</given_name>
                <family_name>Doe</family_name>
                <gender>female</gender>
                <nid>123456</nid>
                <pregnancy_status>suspected</pregnancy_status>
                <forward_to_hie>1</forward_to_hie>
            </update>
        </case>"""
        rv = self.app.post('/forward/', data=data, follow_redirects=True)

if __name__ == '__main__':
    unittest.main()