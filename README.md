# CommCare HQ to OpenHIE Data Forwarding service proof of concept
This project contains a very simple Flask app to receive case data from CommCare HQ
and forward it to and OpenHIE instance.

See [Message specifications for the ICT4H demo](https://jembiprojects.jira.com/wiki/display/ICT4H2013/Message+specifications+for+the+ICT4H+demo)

## Setup
* Create an app on CommCareHQ to create cases with the following properties:
  * given_name
  * family_name
  * dob - date of birth
  * nid - national ID (16 digit string)
  * pregnancy_status - not_pregnant, suspected, confirmed
  * gender - male, female, m, f, M, F
  * forward_to_hie - '1' to forward case data to OpenHIE
* Set up data forwarding of cases to this service
  * https://hostname:port/forward/