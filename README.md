# CommCare HQ to OpenHIE Data Forwarding service proof of concept
This project contains a very simple Flask app to receive case data from CommCare HQ
and forward it to and OpenHIE instance.

See [Message specifications for the ICT4H demo](https://jembiprojects.jira.com/wiki/display/NPRE/Save+Registration+Encounter)

## Setup
* Create an app on CommCareHQ to create cases with the following properties:
  * id_number - the ID number of the patient
  * id_type - the type of ID (see Message specs)
  * id_authority - the issuing authority of the ID (see Message specs)
  * mobile_number - the mobile number formatted as +27554443333
  * given_name
  * family_name
  * dob - date of birth
  * lang_code - preferred language code of the patient
  * facility_id
  * facility_name
  * pregnancy_status - not_pregnant, suspected, confirmed, delivered
  * pregnancy_date - the date associated with the pregnancy (see pregnancy_date_type)
  * pregnancy_date_type
    * edd - estimated deliver date
    * lmp - last mentral period
    * dob - date of birth (when status = delivered)
  * forward_to_hie - '1' to forward case data to OpenHIE
* Set up data forwarding of cases to this service
  * https://hostname:port/forward/
* Mobile workers must have:
  * First name
  * Last name
  * At least one phone number
  * Custom data:
    * hwc_code - Their unique Health Worker Code

See [HIE demo app](https://www.commcarehq.org/exchange/be1cb5a17c9ae6c398f31e38bc82e197/info/) on
 CommCare HQ.
 
 
## Running locally
Create a 'local_config.py' file:

    from config import DevelopmentConfig as DevConfig


    class DevelopmentConfig(DevConfig):
        SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost:5432/hie"
        SECRET_KEY = "123"
        COMMCARE_API_USER = "me@me.com"
        COMMCARE_API_PASSWORD = "my_hq_password"
        COMMCAREHQ_PROJECT = "my_hq_project"
        
Run from the command line:

    > export APP_SETTINGS="local_config.DevelopmentConfig"
    > python run.py