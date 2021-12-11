from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')

class VideoTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Video: {self.video.title}, Tag: {self.tag.name}'

