
from django.contrib import admin
from django.urls import path
from getAudio.views import get_audio
from django.views.generic import TemplateView 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('getAudio/', get_audio, name='get_audio'),
]
