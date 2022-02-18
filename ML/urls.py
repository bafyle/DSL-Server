from django.urls import path
from .views import upload_file_view

urlpatterns = [
    path('uploadfile/', upload_file_view, name='upload-file'),
]