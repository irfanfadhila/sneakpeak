from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Examples:
                  # url(r'^$', 'sisdmcs.views.home', name='home'),
                  # url(r'^blog/', include('blog.urls')),

                  url(r'^admin/', include(admin.site.urls)),
                  url(r'^', include('mainapp.urls', namespace='mainapp')),
                  url(r'^adminsdm', include('adminsdm.urls', namespace='adminsdm')),
                  url(r'^usermgmt', include('usermgmt.urls', namespace='usermgmt')),
                  url(r'^services', include('services.urls', namespace='services')),
                  url(r'^laporan', include('laporan.urls', namespace='laporan')),
                  url(r'^lembur', include('lembur.urls', namespace='lembur')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)