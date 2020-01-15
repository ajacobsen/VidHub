from django.urls import path

from . import views

app_name = 'streamer'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('watch/<watch_id>', views.VideoView.as_view(), name='watch'),
    path('channel/<channel_id>', views.ChannelView.as_view(), name='channel'),
    path('upload/', views.UploadVideoView.as_view(), name='upload'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('like/', views.LikeView.as_view(), name='like'),
    path('dislike/', views.DislikeView.as_view(), name='dislike'),
    path('comment/', views.CommentView.as_view(), name='comment'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/<watch_id>', views.EditVideoView.as_view(), name='edit_video'),
    path('dashboard/delete/', views.DeleteVideoView.as_view(), name='delete_video'),
]