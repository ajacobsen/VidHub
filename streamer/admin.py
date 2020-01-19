from django.contrib import admin

from video_encoding.admin import FormatInline

from .models import Video, VideoFile, Category, Comment, Playlist

@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
   inlines = (FormatInline,)

   list_dispaly = ('get_filename', 'width', 'height', 'duration')
   fields = ('file', 'width', 'height', 'duration')
   readonly_fields = fields

admin.site.register(Video)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Playlist)
