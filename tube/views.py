from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import Video, VideoTag, Tag
from .utils import SearchForm, VideoForm, VideoTagForm, TagForm, CustomTagsForm, UploadVideoForm, open_file
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
from pathlib import Path


# Create your views here.
def index(request):
    if request.method == 'GET':
        query = SearchForm(request.GET)
        if query.is_valid() and 'q' in request.GET:
            videos = Video.objects.filter(title__contains=request.GET.get('q'))
        elif 'tag' in request.GET:
            videos = Video.objects.filter(
                videotag__in=VideoTag.objects.filter(tag__name__contains=request.GET.get('tag')))
        else:
            videos = Video.objects.all()
    return render(request, 'tube/index.html', context={
        'videos': videos
    })


class MySignupView(CreateView):
    form_class = UserCreationForm
    success_url = '/'
    template_name = 'tube/signup.html'


class MyLoginView(LoginView):
    template_name = 'tube/login.html'

    def post(self, request, **kwargs):
        if not self.request.user.is_anonymous:
            redirect(request.POST.get('next'))
        return super().post(request, **kwargs)


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #  log the user in
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'tube/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'tube/login.html', {'form': form})


class MyLogoutView(LogoutView):
    template_name = 'tube/login.html'


class MyUploadView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tube/upload.html', context={
            'tags_form': CustomTagsForm(),
            'video_form': UploadVideoForm()
        })

    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        tags_form = CustomTagsForm(request.POST)
        video_form = UploadVideoForm(request.POST, request.FILES)
        video_form.is_valid()
        if tags_form.is_valid() and video_form.is_valid():
            tags = tags_form.cleaned_data['tags'].split(" ")
            video = Video()
            video.title = video_form.cleaned_data['title']
            video.file = request.FILES.get('video')
            video.save()
            if tags:
                for a_tag in tags:
                    tag_inst = Tag.objects.get_or_create(name=a_tag)[0]
                    VideoTag.objects.create(tag=tag_inst, video=video)
            else:
                VideoTag.objects.create(video=video)
        return redirect('index')


class MyWatchView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        video = get_object_or_404(Video, id=id)
        tags = Tag.objects.all()
        video_file_name = Path(video.file.name).name
        return render(request, 'tube/watch.html', context={
            'video': video,
            'tags': tags,
            'video_file_name': video_file_name
        })


class MyStreamView(View):
    def get(self, request, *args, **kwargs):
        filename = kwargs['filename']
        # video = get_object_or_404(Video, title=title)
        file, status_code, content_length, content_range = open_file(request, filename)
        response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(content_length)
        response['Cache-Control'] = 'no-cache'
        response['Content-Range'] = content_range
        return response

### same as MyStreamView but much simplier
# def play_view(request, name):
#     with open(os.path.join(settings.MEDIA_ROOT, name), "rb") as f:
#         file = f.read()
#     response = HttpResponse(file, content_type="video/mp4")
#     response["Accept-Ranges"] = "bytes"
#     return response
