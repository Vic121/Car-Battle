# management/commands/fbshell.py
import os
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.conf import settings

from facebook import Facebook


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
                    help='Tells Django to use plain Python, not IPython.'),
    )
    help = "Runs a Python interactive interpreter with an active facebook" \
           "session. Tries to use IPython, if it's available."

    requires_model_validation = False

    def _start_fb_session(self):
        api_key = settings.FACEBOOK_API_KEY
        secret_key = settings.FACEBOOK_SECRET_KEY
        app_name = getattr(settings, 'FACEBOOK_APP_NAME', None)
        callback_path = getattr(settings, 'FACEBOOK_CALLBACK_PATH', None)
        internal = getattr(settings, 'FACEBOOK_INTERNAL', True)
        proxy = getattr(settings, 'HTTP_PROXY', None)
        facebook = Facebook(api_key, secret_key, app_name=app_name,
                            internal=internal, callback_path=callback_path,
                            proxy=proxy)
        facebook.auth.createToken()
        # Show login window
        # Set popup=True if you want login without navigational elements
        facebook.login()
        # Login to the window, then press enter
        print 'After logging in, press enter...'
        raw_input()
        facebook.auth.getSession()
        print 'Session Key:   ', facebook.session_key
        print 'Your UID:      ', facebook.uid
        info = facebook.users.getInfo([facebook.uid], ['name', 'birthday', 'affiliations', 'sex'])[0]
        print 'Hi ', info['name']
        return facebook

    def handle_noargs(self, **options):
        facebook = self._start_fb_session()
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models

        loaded_models = get_models()

        use_plain = options.get('plain', False)

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError
            import IPython
            # Explicitly pass an empty list as arguments, because otherwise IPython
            # would use sys.argv from this script.
            local_dict = dict(facebook=facebook)
            shell = IPython.Shell.IPShell(argv=[], user_ns=local_dict)
            shell.mainloop()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try:  # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter

                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            imported_objects['facebook'] = facebook
            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain:
                pythonrc = os.environ.get("PYTHONSTARTUP")
                if pythonrc and os.path.isfile(pythonrc):
                    try:
                        execfile(pythonrc)
                    except NameError:
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)
