from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core.views import test_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("test/", test_view),

    path("api/", include("user_auth_app.urls")),
    path("api/video/", include("videoflix_app.urls")),

] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('/video/', document_root=settings.MEDIA_ROOT / 'video')


