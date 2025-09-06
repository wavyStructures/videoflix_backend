# videoflix_app/views.py
import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Video
from .serializers import VideoSerializer


# class VideoListView(APIView):
#     permission_classes = [IsAuthenticated]  # JWT required

#     def get(self, request):
#         videos = Video.objects.all()
#         serializer = VideoSerializer(videos, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

class VideoListView(ListAPIView):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer


class HLSIndexView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        # Path: MEDIA_ROOT/hls/<movie_id>/<resolution>/index.m3u8
        playlist_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(movie_id), resolution, 'index.m3u8')

        if not os.path.exists(playlist_path):
            raise Http404("Playlist not found")

        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSChunkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        segment_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(movie_id), resolution, segment)

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')



# class VideoListView(APIView):
#     def get(self, request):
#         dummy_videos = [
#             {"id": 1, "title": "Django for Beginners"},
#             {"id": 2, "title": "REST APIs with DRF"},
#         ]
#         return Response(dummy_videos, status=status.HTTP_200_OK)

# class HLSIndexView(APIView):
#     def get(self, request, movie_id, resolution):
#         return Response({
#             "message": f"Returning index.m3u8 for movie {movie_id} at {resolution}"
#         }, status=status.HTTP_200_OK)

# class HLSChunkView(APIView):
#     def get(self, request, movie_id, resolution, segment):
#         return Response({
#             "message": f"Returning segment {segment} for movie {movie_id} at {resolution}"
#         }, status=status.HTTP_200_OK)
