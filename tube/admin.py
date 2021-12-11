from django.contrib import admin
from .models import Tag, VideoTag, Video

admin.site.register(Video)
admin.site.register(VideoTag)
admin.site.register(Tag)


# Register your models here.
