import re
from django import forms
from .models import *
from pathlib import Path
from typing import IO, Generator
from django.shortcuts import get_object_or_404
from django.conf import settings


class SearchForm(forms.Form):
    q = forms.CharField(max_length=255)

class UploadVideoForm(forms.Form):
    video = forms.FileField(label='Video')
    title = forms.CharField(max_length=255)

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'file']
        labels = {
            'file': 'video'
        }


class VideoTagForm(forms.ModelForm):
    class Meta:
        model = VideoTag
        fields = '__all__'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'


class CustomTagsForm(forms.Form):
    tags = forms.RegexField(r'^\s*[A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*\s*$')

def ranged(
        file: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()


def open_file(request, filename):
    # _video = get_object_or_404(Video, pk=video_pk)

    path = Path(settings.MEDIA_ROOT, 'uploads', filename)

    file = path.open('rb')
    file_size = path.stat().st_size

    content_length = file_size
    status_code = 200
    content_range = request.headers.get('range')

    if content_range is not None:
        content_ranges = content_range.strip().lower().split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
        content_length = (range_end - range_start) + 1
        file = ranged(file, start=range_start, end=range_end + 1)
        status_code = 206
        content_range = f'bytes {range_start}-{range_end}/{file_size}'

    return file, status_code, content_length, content_range
