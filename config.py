import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    COMMCARE_API_ROOT='https://www.commcarehq.org',
    COMMCARE_API_USER='demo'
    COMMCARE_API_PASSWORD='demo'
    COMMCAREHQ_PROJECT='demo'
    HIE_USERNAME='test'
    HIE_PASSWORD='test'
    HIE_URL_BASE='https://sandbox-him.jembi.org:5000'
    HIE_REGISTER_URL='/ws/rest/v1/registration/net.ihe/DocumentDossier'
    HIE_VALIDATE_URL='/ws/rest/v1/registration/validate'


class ProductionConfig(Config):
    DEBUG = False
    COMMCARE_API_USER=os.environ.get('COMMCARE_API_USER', '')
    COMMCARE_API_PASSWORD=os.environ.get('COMMCARE_API_PASSWORD', '')
    COMMCAREHQ_PROJECT=os.environ.get('COMMCAREHQ_PROJECT', '')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True