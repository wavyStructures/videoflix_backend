from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VideoListView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    
    
class HLSIndexView(APIView):
    def get(self, request, movie_id, resolution):
        return Response(status=status.HTTP_200_OK)
    
    
class HLSChunkView(APIView):
    def get(self, request, movie_id, resolution, segment):
        return Response(status=status.HTTP_200_OK)
    
    

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
