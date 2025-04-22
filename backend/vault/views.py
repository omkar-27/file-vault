import os
from datetime import datetime

from django.http import HttpResponse, Http404, FileResponse
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .models import File
from .serializers import FileSerializer


def index(request):
    return HttpResponse("Welcome to the Vault!")


class FileListPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        file_hash = File.calculate_hash(file_content)
        uploaded_file.seek(0)

        existing_file = File.objects.filter(file_hash=file_hash, is_duplicate=False).first()
        if existing_file:
            duplicate = File.objects.create(
                file=existing_file.file,
                filename=uploaded_file.name,
                size=existing_file.size,
                file_hash=file_hash,
                is_duplicate=True,
                original_file=existing_file
            )
            serializer = FileSerializer(duplicate)
            return Response(
                {'message': 'Duplicate file, stored as reference.', 'file': serializer.data},
                status=status.HTTP_201_CREATED
            )

        serializer = FileSerializer(data={
            'file': uploaded_file,
            'filename': uploaded_file.name,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'File uploaded successfully.', 'file': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileListView(APIView):
    pagination_class = FileListPagination

    def get(self, request):
        queryset = File.objects.all()

        # Filters
        filename = request.query_params.get('filename')
        file_hash = request.query_params.get('file_hash')
        min_size = request.query_params.get('min_size')
        max_size = request.query_params.get('max_size')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        sort_by = request.query_params.get('sort_by', 'uploaded_at')
        order = request.query_params.get('order', 'desc')

        if filename:
            queryset = queryset.filter(filename__icontains=filename)
        if file_hash:
            queryset = queryset.filter(file_hash=file_hash)
        if min_size:
            queryset = queryset.filter(size__gte=int(min_size))
        if max_size:
            queryset = queryset.filter(size__lte=int(max_size))
        if start_date:
            queryset = queryset.filter(uploaded_at__gte=datetime.fromisoformat(start_date))
        if end_date:
            queryset = queryset.filter(uploaded_at__lte=datetime.fromisoformat(end_date))

        # Sorting
        if sort_by in ['uploaded_at', 'size']:
            sort_order = sort_by if order == 'asc' else f'-{sort_by}'
            queryset = queryset.order_by(sort_order)

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = FileSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data)


class FileDeleteView(APIView):
    def delete(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except File.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


class FileDownloadView(APIView):
    def get(self, request, pk):
        try:
            file_obj = File.objects.get(pk=pk)
            file_path = file_obj.file.path

            if not os.path.exists(file_path):
                raise Http404("File not found on disk")

            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{file_obj.filename}"'
            return response

        except File.DoesNotExist:
            raise Http404("File not found")


@api_view(['GET'])
def storage_summary(request):
    total_files = File.objects.count()
    logical_storage = sum(file.size for file in File.objects.all())
    physical_storage = sum(file.size for file in File.objects.filter(is_duplicate=False))

    saved_bytes = logical_storage - physical_storage
    saved_percent = (saved_bytes / logical_storage) * 100 if logical_storage else 0

    return Response({
        'total_files': total_files,
        'logical_storage_kb': round(logical_storage / 1024, 2),
        'physical_storage_kb': round(physical_storage / 1024, 2),
        'saved_kb': round(saved_bytes / 1024, 2),
        'efficiency_percent': round(saved_percent, 2)
    })
