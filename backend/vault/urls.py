from django.urls import path
from .views import (
    index,
    FileUploadView,
    FileListView,
    FileDeleteView,
    FileDownloadView,
    storage_summary,
)

urlpatterns = [
    path('', index, name='index'),  # Default view
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('files/<int:pk>/', FileDeleteView.as_view(), name='file-delete'),
    path('download/<int:pk>/', FileDownloadView.as_view(), name='file-download'),
    path('storage-summary/', storage_summary, name='storage-summary'),
]