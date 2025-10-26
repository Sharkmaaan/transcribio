from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_video, name='upload_video'),
    path('status/<int:pk>/', views.transcription_status, name='transcription_status'),
    path('download/<int:pk>/<str:transcript_type>/', views.download_transcript, name='download_transcript'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('signup/', views.signup, name='signup'), 

]