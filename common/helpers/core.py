from django.core.urlresolvers import reverse as reverse_org
from django.conf import settings


def reverse(view, args=None, kwargs=None):
    return reverse_org(view, args=args, kwargs=kwargs)


# --- Others

def facebook_require_login(next=None, internal=None):
    """
    Decorator for Django views that requires the user to be logged in.
    The FacebookMiddleware must be installed.

    Standard usage:
        @facebook_require_login()
        def some_view(request):
            ...

    Redirecting after login:
        To use the 'next' parameter to redirect to a specific page after login, a callable should
        return a path relative to the Post-add URL. 'next' can also be an integer specifying how many
        parts of request.path to strip to find the relative URL of the canvas page. If 'next' is None,
        settings.callback_path and settings.app_name are checked to redirect to the same page after logging
        in. (This is the default behavior.)
        @require_login(next=some_callable)
        def some_view(request):
            ...
    """

    def decorator(view):

        def newview(request, *args, **kwargs):

            # if not request.engine.IS_FB:
            return view(request, *args, **kwargs)

            next = newview.next
            internal = newview.internal

            try:
                fb = request.facebook
            except:
                raise ImproperlyConfigured('Make sure you have the Facebook middleware installed.')

            if internal is None:
                internal = request.facebook.internal

            if callable(next):
                next = next(request.path)
            elif isinstance(next, int):
                next = '/'.join(request.path.split('/')[next + 1:])
            elif next is None and fb.callback_path and request.path.startswith(fb.callback_path):
                next = request.path[len(fb.callback_path):]
            elif not isinstance(next, str):
                next = ''

            if not fb.check_session(request) or (
                            request.method == 'POST' and not request.POST.has_key('fb_sig_session_key')):
                # If user has never logged in before, the get_login_url will redirect to the TOS page
                return fb.redirect(fb.get_login_url(next=next))

            if internal and request.method == 'GET' and fb.app_name:
                return fb.redirect('%s%s' % (fb.get_app_url(), next))

            return view(request, *args, **kwargs)

        newview.next = next
        newview.internal = internal

        return newview

    return decorator


def request_logger(view):
    # return view
    def wrapper(request, *args, **kw):
        # logger.info(
        #	 "%s, G=%s, P=%s, C=%s, M=%s", request.path, request.GET,
        #	 request.POST, request.COOKIES, request.META
        # )
        logger.info(
            "%s, G=%s, P=%s, C=%s", request.path, request.GET,
            request.POST, request.COOKIES
        )
        return view(request, *args, **kw)

    return wrapper


def get_invite_cookie(request, response, user):
    if request.COOKIES.get('invitee_id') is not None and request.COOKIES.get('invitee_id') != '0':

        try:
            invitee_id = int(request.COOKIES.get('invitee_id'))
        except ValueError:
            response.set_cookie('invitee_id', 0)
            return

        if request.__dict__.has_key('facebook'):
            # zapraszanie siebie?
            if invitee_id == int(user.fb_id):
                response.set_cookie('invitee_id', 0)
                return

            # nieznany user?
            from userprofile.models import UserProfile

            if UserProfile.objects.get_by_fb_id(invitee_id) is None:
                response.set_cookie('invitee_id', 0)
                return

            from family.models import UserInvite

            ui = UserInvite.objects.get_by_user(invitee_id)
            ui.send_invites((str(user.fb_id),))
        else:
            # nieznany user?
            from userprofile.models import UserProfile

            if UserProfile.objects.get_by_id(invitee_id) is None:
                response.set_cookie('invitee_id', 0)
                return

            from family.models import UserInviteWeb

            ui = UserInviteWeb.objects.get_by_user(invitee_id)
            ui.send_invites((str(user.id),))

        response.set_cookie('invitee_id', 0)


from django.db.models import AutoField


def copy_model_instance(obj):
    """Create a copy of a model instance.

    M2M relationships are currently not handled, i.e. they are not
    copied.

    See also Django #4027.
    """
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and \
                    not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


def is_number(s):
    """Is this the right way for checking a number.
    Maybe there is a better pythonic way :-)"""
    try:
        int(s)
        return True
    except TypeError:
        pass
    except ValueError:
        pass
    return False


def exp_mod(my_lvl, other_lvl):
    if my_lvl > other_lvl:
        sign = '-'
    elif my_lvl == other_lvl:
        sign = ''
    else:
        sign = '+'

    try:
        val = settings.EXP_MOD[sign + str(abs(my_lvl - other_lvl))]
    except KeyError:
        val = settings.EXP_MOD[sign + 'x']

    if val == 0:
        return 0
    return val / 100.0
