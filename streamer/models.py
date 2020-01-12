# from datetime import date, datetime
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from video_encoding.fields import VideoField
from video_encoding.models import Format
from users.models import Channel

class Category(models.Model):
	title = models.CharField(max_length=100)
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.title

class Video(models.Model):
	VIDEO_STATUS_CHOICES = (
		('public', 'public'),
		('private', 'private'),
		('unlisted', 'unlisted'),
		('drafting', 'drafting'),
	)

	VIDEO_TYPE_CHOICES = (
		('local', 'Local file'),
		('remote', 'Remote file'),
		('embed', 'From YouTube'),
	)

	watch_id = models.CharField(max_length=10, blank=True)
	title = models.CharField(max_length=100, blank=True)
	description = models.TextField(blank=True, null=True)
	status = models.CharField(max_length=8, choices=VIDEO_STATUS_CHOICES, blank=True)
	view_count = models.BigIntegerField(default=0)
	video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES, default='local')
	uploaded = models.DateTimeField(default=timezone.now)
	width = models.PositiveIntegerField(editable=False, null=True)
	height = models.PositiveIntegerField(editable=False, null=True)
	duration = models.FloatField(editable=False, null=True)
	thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
	file = VideoField(width_field='width', height_field='height', duration_field='duration')
	format_set = GenericRelation(Format)
	processed = models.BooleanField(default=False)

	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return str(self.file)

class PlaylistEntry(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	date_added = models.DateTimeField(default=timezone.now)

class Playlist(models.Model):
	title = models.CharField(max_length=100)
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
	videos = models.ManyToManyField(PlaylistEntry)

	def __str__(self):
		return '{} from {}'.format(self.title, self.channel.name)


class Subscription(models.Model):
	from_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="subscriber")
	to_channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

class Likes(models.Model):
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
	video = models.ForeignKey(Video, on_delete=models.CASCADE)

class Dislikes(models.Model):
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
	video = models.ForeignKey(Video, on_delete=models.CASCADE)

class Comment(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
	text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

	class Meta:
		ordering = ('created',)