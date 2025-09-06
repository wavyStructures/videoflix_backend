from django.urls import path
from .views import VideoListView, HLSIndexView, HLSChunkView

urlpatterns = [
    path('', VideoListView.as_view(), name='video-list'),
    path('<int:movie_id>/<str:resolution>/index.m3u8', HLSIndexView.as_view(), name='hls-index'),
    path('<int:movie_id>/<str:resolution>/<str:segment>/', HLSChunkView.as_view(), name='hls-chunk'),
]

