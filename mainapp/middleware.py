__author__ = 'afifun'

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.views import logout

class SessionExpiredMiddleware:
    def process_request(self, request):

        if  request.user.is_authenticated():
            try:
                last_activity = request.session['last_activity']
                now = timezone.now()

                print (now - last_activity)
                if now - last_activity > timedelta( 0, 1440 * 60, 0):
                    print ('session harusnya expired')
                    del request.session['last_activity']
                    logout(request)
                    return
            except KeyError:
                pass
            request.session['last_activity'] = timezone.now()
        else:
            return