from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('tube/', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('tube/upload/', views.MyUploadView.as_view(), name='upload'),
    path('tube/watch/stream/<str:filename>/', views.MyStreamView.as_view(), name='stream'),
    path('tube/watch/<int:pk>/', views.MyWatchView.as_view(), name='watch')
]
