import base64

from django.conf import settings


class Twitter(object):
    """Send messages through TWITTER"""

    def __init__(self, profile='twitter'):
        self.username = settings.IM[profile]['username']
        self.password = settings.IM[profile]['password']

    def send(self, msg):
        import urllib2, urllib

        twitter_status = msg

        request = urllib2.Request('http://twitter.com/statuses/update.json')
        request.headers['Authorization'] = 'Basic %s' % (base64.b64encode(self.username + ':' + self.password),)
        request.data = urllib.urlencode({'status': twitter_status})
        response = urllib2.urlopen(request)

        print response.read()
