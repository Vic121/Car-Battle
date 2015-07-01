import logging
import hashlib

# from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth import login, get_backends
from django.http import HttpResponseRedirect

from userprofile.models import UserProfile


class fbMiddleware(object):
    """
    Handle Facebook association, autologin
    """

    def process_request(self, request):
        request.fbc_uid = None
        request.fbc_token = None
        f_name = False
        l_name = False

        # Check if we have the FBConnect cookie
        if 'fbs_%s' % settings.FACEBOOK_APP_ID in request.COOKIES and self.get_facebook_signature(request.COOKIES):
            # get the FB user ID from cookie
            (request.fbc_token, request.fbc_uid) = self.get_facebook_signature(request.COOKIES)

            request.engine.IS_FBC = True
            if not request.fbc_uid or request.engine.IS_FB: return None

            try:
                f = UserProfile.objects.get(partner='fb', partner_login=request.fbc_uid)
            except Exception, e:
                if not request.GET.has_key('reg_fbc'):
                    return HttpResponseRedirect('/?reg_fbc=1')
            else:
                if not hasattr(request.engine, 'user'):
                    # update avatar
                    import Image, urllib2, os

                    try:
                        path = settings.MEDIA_ROOT + 'avatars/' + str(f.user_id / 1000)
                        if not os.path.isdir(path):
                            os.makedirs(path, 0777)
                        image = '%s/%s.jpg' % (path, str(f))
                        img = urllib2.urlopen('http://graph.facebook.com/%s/picture' % request.fbc_uid).read()
                        tmp = open('%s/%s.jpg' % (path, str(f)), 'wb')
                        tmp.write(img)
                        tmp.close()
                        f.avatar = '%s/%s.jpg' % (str(f.user_id / 1000), str(f))
                        f.save()

                    except Exception, e:
                        logging.warning("Could not save avatar from Facebook")
                        logging.warning(e)

                    # authenticate
                    backend = get_backends()[0]
                    f.user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
                    login(request, f.user)

                    return HttpResponseRedirect('/')
        else:
            # not fb connect session
            pass

    def get_facebook_signature(self, cookie):
        signature_keys = []
        cookies = cookie.get('fbs_' + settings.FACEBOOK_APP_ID).split('&')
        uid, token = None, None

        # print sorted(cookies)
        for c in sorted(cookies):
            k, v = c.split('=')
            if k == 'sig': continue
            if k == 'uid': uid = v
            if k == 'access_token': token = v

            signature_keys.append('%s=%s' % (k, v))

        signature_string = '&'.join(signature_keys) + settings.FACEBOOK_SECRET_KEY

        h = hashlib.md5()
        h.update(signature_string)
        # print h.hexdigest()

        # datetime.fromtimestamp(float(request.COOKIES[settings.FACEBOOK_APP_ID+'_expires'])) > datetime.now()

        if not uid or not token:
            logging.error('Not uid and/or token. %s/%s. %s' % (uid, token, signature_string))

        return (token, uid)
