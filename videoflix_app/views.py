from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from user_auth_app.authentication import CookieJWTAuthentication
from .models import Video
from .serializers import VideoSerializer
from .utils import safe_media_path, validate_segment_name


class VideoListView(ListAPIView):
    """
    API endpoint that provides a list of all available videos.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer


class HLSIndexView(APIView):
    """
    Serves the HLS playlist file (.m3u8) for a given video and resolution.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        playlist_path = safe_media_path("hls", str(movie_id), resolution, "index.m3u8")

        if not playlist_path.exists():
            raise Http404("Playlist not found")

        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSChunkView(APIView):
    """
    Serves individual HLS video segments (.ts files).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        segment = validate_segment_name(segment)
        segment_path = safe_media_path('hls', str(movie_id), resolution, segment)

        if not segment_path.exists():
            raise Http404("Segment not found")

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')

