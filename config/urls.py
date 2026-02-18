from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve # Required for manual serving

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('', include('courses.urls')),
    
    # FORCE DJANGO TO SERVE MEDIA IN PRODUCTION
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]