from django.conf import settings
from django.http import HttpResponseRedirect


class EngineMiddleware(object):
    def __init__(self, api_key=None, secret_key=None, app_name=None, callback_path=None, internal=None):
        self.api_key = api_key or getattr(settings, 'FACEBOOK_API_KEY', None)
        self.secret_key = secret_key or getattr(settings, 'FACEBOOK_SECRET_KEY', None)
        self.app_name = app_name or getattr(settings, 'FACEBOOK_APP_NAME', None)
        self.callback_path = callback_path or getattr(settings, 'FACEBOOK_CALLBACK_PATH', None)
        self.internal = internal or getattr(settings, 'FACEBOOK_INTERNAL', True)
        self.proxy = None
        if getattr(settings, 'USE_HTTP_PROXY', False):
            self.proxy = settings.HTTP_PROXY

    def process_request(self, request):
        if request.META['PATH_INFO'].find('/static/') > -1: return None
        if request.META['PATH_INFO'].find('/images/') > -1: return None
        if request.META['PATH_INFO'] == '/favicon.ico': return HttpResponseRedirect('/static/images/favicon.ico')
        if request.META['PATH_INFO'] == '/robots.txt': return HttpResponseRedirect('/static/robots.txt')

        if settings.PROJECT_NAME == 'Crime Corp':
            from crimecorp.engine.engine import Engine

            engine = Engine(request)

            if request.META['SERVER_NAME'] == 'fb.crimecorp.com':
                engine.IS_FB = True
            else:
                engine.IS_FB = False

            engine.start()
            request.engine = engine

        elif settings.PROJECT_NAME == 'Car Battle':
            from common.engine import Engine

            engine = Engine(request)

            # if request.META['SERVER_NAME'] == 'madfb.com':
            # engine.IS_FB = True
            # elif request.META['SERVER_NAME'] == 'fb.car-battle.com':
            # engine.IS_PARTNER = True
            # engine.IS_FB = True
            # elif request.META['SERVER_NAME'] in ('www.car-battle.com', 'car-battle.com') and 'fbs_225960433127' in request.COOKIES.keys():
            # engine.IS_FBC = True
            # else:
            # if request.META['SERVER_NAME'] == 'partner.car-battle.com':
            # engine.IS_PARTNER = True

            engine.start()
            request.engine = engine

        elif settings.PROJECT_NAME == 'Scores':
            from scores.engine.engine import Engine

            engine = Engine(request)

            if request.META['SERVER_NAME'] == 'fb.pickscore.net':
                engine.IS_FB = True
            else:
                if request.META['SERVER_NAME'] == 'partner.pickscore.net':
                    engine.IS_PARTNER = True

            engine.start()
            request.engine = engine

        else:
            from common.engine.engine import Engine

        if not hasattr(request, 'engine'):
            request.engine = Engine(request)

        return None

    def process_response(self, request, response):

        # try:
        # 	if not settings.LOCAL and hasattr(request, 'engine') and response.status_code >= 500:
        # 		request.engine.send_mail(['marek.mikuliszyn@gmail.com'], str(response.status_code), response.content, mime='html')
        # 		logging.warning(response.content)
        # except AttributeError:
        # 	request.engine.send_mail(['marek.mikuliszyn@gmail.com'], 'Error with status unknown', '', mime='html')

        # if not self.internal and request.facebook.session_key and request.facebook.uid:
        # 	request.session['facebook_session_key'] = request.facebook.session_key
        # 	request.session['facebook_user_id'] = request.facebook.uid

        # response['Access-Control-Allow-Origin'] = '*'
        # response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        # response['Access-Control-Max-Age'] = 1000
        # response['Access-Control-Allow-Headers'] = '*'

        return response


def output_function(o):
    return str(type(o))


class ProfilerMiddleware(object):
    """
    Measure memory taken by requested view, and response
    """

    def process_request(self, request):
        req = request.META['PATH_INFO']
        if req.find('static') == -1:
            self.start_objects = muppy.get_objects()

    def process_response(self, request, response):
        req = request.META['PATH_INFO']
        if req.find('static') == -1:
            print req
            self.end_objects = muppy.get_objects()
            sum_start = summary.summarize(self.start_objects)
            sum_end = summary.summarize(self.end_objects)
            diff = summary.get_diff(sum_start, sum_end)
            summary.print_(diff)
            # print '~~~~~~~~~'
            # cb = refbrowser.ConsoleBrowser(response, maxdepth=2, str_func=output_function)
            # cb.print_tree()
            print '~~~~~~~~~'
            a = asizeof(response)
            print 'Total size of response object in kB: %s' % str(a / 1024.0)
            print '~~~~~~~~~'
            a = asizeof(self.end_objects)
            print 'Total size of end_objects in MB: %s' % str(a / 1048576.0)
            b = asizeof(self.start_objects)
            print 'Total size of start_objects in MB: %s' % str(b / 1048576.0)
            print '~~~~~~~~~'
        return response
