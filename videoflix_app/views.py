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