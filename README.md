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
  * language_code - preferred language code of the patient
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

See [HIE demo app](https://www.commcarehq.org/exchange/be1cb5a17c9ae6c398f31e38bc82e197/info/) on
 CommCare HQ.