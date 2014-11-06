# Borrowed from https://github.com/dimagi/commcare-export/blob/master/commcare_export/commcare_hq_client.py

from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import requests
import logging

# This import pattern supports Python 2 and 3
from requests.auth import HTTPDigestAuth

AUTH_MODE_SESSION = 'session'
AUTH_MODE_DIGEST = 'digest'

try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urlencode, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib import urlopen, urlencode

logger = logging.getLogger(__file__)

LATEST_KNOWN_VERSION='0.5'

import hie_connect


class RepeatableIterator(object):
    """
    Pass something iterable into this and,
    unless it has crufty issues, voila.
    """

    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self.generator()

    @classmethod
    def to_jvalue(cls, obj):
        if isinstance(obj, cls):
            return list(obj)
        raise TypeError(repr(obj) + 'is not JSON serializable')


class CommCareHqClient(object):
    """
    A connection to CommCareHQ for a particular version, project, and user.
    """

    def __init__(self, url, project, version=LATEST_KNOWN_VERSION, session=None, auth=None):
        self.version = version
        self.url = url
        self.project = project
        self.__session = session
        self.__auth = auth

    @property
    def session(self):
        if self.__session == None:
            self.__session = requests.Session(headers={'User-Agent': 'hie-connect/%s' % hie_connect.__version__})
        return self.__session

    def api_url(self, project):
        return '%s/a/%s/api/v%s' % (self.url, project or self.project, self.version)

    def authenticated(self, username=None, password=None, mode=AUTH_MODE_SESSION):
        """
        Returns a freshly authenticated CommCareHqClient with a new session.
        This is safe to call many times and each of the resulting clients
        remain independent, so you can log in with zero, one, or many users.
        """

        session = requests.Session()
        auth = None
        if mode == AUTH_MODE_SESSION:
            login_url = '%s/accounts/login/' % self.url

            # Pick up things like CSRF cookies and form fields by doing a GET first
            response = session.get(login_url)
            if response.status_code != 200:
                raise Exception('Failed to connect to authentication page (%s): %s' % (response.status_code, response.text))

            response = session.post(login_url,
                                    headers = {'Referer': login_url },
                                    data = {'username': username,
                                            'password': password,
                                            'csrfmiddlewaretoken': response.cookies['csrftoken']})
            if response.status_code != 200:
                raise Exception('Authentication failed (%s): %s' % (response.status_code, response.text))

        elif mode == 'digest':
            auth = HTTPDigestAuth(username, password)
        else:
            raise Exception('Unknown auth mode: %s' % mode)

        return CommCareHqClient(url=self.url, project=self.project, version=self.version, session=session, auth=auth)

    def get(self, resource, id=None, params=None, project=None):
        """
        Gets the named resource.

        Currently a bit of a vulnerable stub that works
        for this particular use case in the hands of a trusted user; would likely
        want this to work like (or via) slumber.
        """
        resource_url = '%s/%s/' % (self.api_url(project), resource)
        if id:
            resource_url = '%s%s/' % (resource_url, id)
        response = self.session.get(resource_url, params=params, auth=self.__auth)

        if response.status_code != 200:
            raise Exception('GET %s failed (%s): %s' % (resource_url, response.status_code, response.text))
        else:
            return response.json()
            
    def iterate(self, resource, params=None):
        """
        Assumes the endpoint is a list endpoint, and iterates over it
        making a lot of assumptions that it is like a tastypie endpoint.
        """
        params = dict(params or {})
        def iterate_resource(resource=resource, params=params):
            more_to_fetch = True

            while more_to_fetch:
                batch = self.get(resource, params)
                logger.debug('Received %s-%s of %s', 
                             batch['meta']['offset'], 
                             int(batch['meta']['offset'])+int(batch['meta']['limit']),
                             int(batch['meta']['total_count']))

                if not batch['objects']:
                    more_to_fetch = False
                else:
                    for obj in batch['objects']:
                        yield obj

                    if batch['meta']['next']:
                        params = parse_qs(urlparse(batch['meta']['next']).query)
                    else:
                        more_to_fetch = False
                
        return RepeatableIterator(iterate_resource)


class MockCommCareHqClient(object):
    """
    An in-memory mock of the hq client, instantiated
    with a simple mapping of resource and params to results.

    Since dictionaries are not hashable, the mapping is
    written as a pair of tuples, handled appropriately
    internallly.

    MockCommCareHqClient({
        'forms': [
            (
                id, # or None
                {'_search': 'test1'},
                [
                   ... objects ...
                ]
            ),
        ]
    })
    """    
    def __init__(self, mock_data):
        self.mock_data = dict([(resource, dict([(params if isinstance(params, basestring) else urlencode(params), result) for params, result in resource_results]))
                              for resource, resource_results in mock_data.items()])

    def authenticated(self, *args, **kwargs):
        return self

    def get(self, resource, id=None, params=None, project=None):
        if id:
            return self.mock_data[resource][id]
        elif params:
            return self.mock_data[resource][urlencode(params)]
    
    def iterate(self, resource, params=None):
        return self.mock_data[resource][urlencode(params)]

