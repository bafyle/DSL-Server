from django.urls import path
from .views import upload_media_view

urlpatterns = [
    path('upload-media/', upload_media_view, name='upload-media'),
]