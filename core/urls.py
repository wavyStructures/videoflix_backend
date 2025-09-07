"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core.views import test_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("test/", test_view),

    # API endpoints
    path("api/auth/", include("user_auth_app.urls")),
    path("api/video/", include("videoflix_app.urls")),

    # HLS static files (served from MEDIA_ROOT/videos)
    re_path(r"^videos/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT / "videos"}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from core.views import test_view
# from django.urls import re_path


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('test/', test_view),
#     path('api/', include('user_auth_app.urls')),
#     # path('api/', include('videoflix_app.urls')),

#     # path('api/auth/', include('user_auth_app.urls')),
#     path('api/video/', include('videoflix_app.urls')),
#     re_path(r'^api/video/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT / 'videos'}),

# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    

