import httplib
import base64

import simplejson as json
from django.conf import settings


class Blip(object):
    """Send messages through BLIP"""

    def __init__(self, profile='blip'):
        self.username = settings.IM[profile]['username']
        self.password = settings.IM[profile]['password']

    def send(self, msg):
        http_url = 'http://api.blip.pl/updates'
        API_HEADERS = {
            'Content-Type': 'application/json',
            'X-Blip-api': '0.02',
            'User-Agent': 'BLIP API',
            'Authorization': 'Basic %s' % (base64.b64encode(self.username + ':' + self.password))
        }

        update = {}
        update['body'] = msg

        post_params = json.dumps(update)

        connection = httplib.HTTPConnection('api.blip.pl')
        connection.request('POST', http_url, headers=API_HEADERS, body=post_params)

        response = connection.getresponse()
        # headers = response.getheaders()
        # status = response.status

        print response.read()
