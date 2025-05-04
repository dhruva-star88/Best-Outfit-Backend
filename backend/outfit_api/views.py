import os
import shutil
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.conf import settings

from .pipeline import process_uploaded_images, load_closet, save_closet, recommend_best_outfit, remove_duplicates

IMAGE_FOLDER = os.path.join(settings.BASE_DIR, 'images')
CLOSET_FILE = os.path.join(settings.BASE_DIR, 'closet.json')

class UploadView(APIView):
    parser_classes = [parsers.MultiPartParser]

    def post(self, request, format=None):
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)

        for image in request.FILES.getlist('images'):
            with open(os.path.join(IMAGE_FOLDER, image.name), 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)

        process_uploaded_images(image_folder=IMAGE_FOLDER)

        return Response({'message': 'Images processed and closet updated.'}, status=status.HTTP_201_CREATED)

class ClosetView(APIView):
    def get(self, request):
        closet = load_closet()
        return Response(closet)

    def delete(self, request):
        if os.path.exists(CLOSET_FILE):
            os.remove(CLOSET_FILE)
        if os.path.exists(IMAGE_FOLDER):
            shutil.rmtree(IMAGE_FOLDER)
        return Response({'message': 'Closet and images cleared.'})

class RecommendView(APIView):
    def get(self, request):
        closet = load_closet()
        outfits = recommend_best_outfit(closet)
        unique_outfits = remove_duplicates(outfits)
        return Response(unique_outfits)
