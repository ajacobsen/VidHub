import os
import shutil
import logging
import magic

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.conf import settings
from django.views.decorators.vary import vary_on_headers
from django.forms.models import model_to_dict
from django.core.files.images import ImageFile
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.template.loader import get_template

from video_encoding.backends.ffmpeg import FFmpegBackend
from video_encoding.exceptions import FFmpegError
from video_encoding import tasks
from django_rq import enqueue

from users.models import Channel

from .models import Video, Category, Playlist, PlaylistEntry, Subscription, Likes, Dislikes, Comment
from .forms import VideoForm, EditVideoForm
from .tokens import user_tokenizer

logger =logging.getLogger('django')

def index(request):
	categories = Category.objects.all()
	context = {'categories' : categories }
	search=request.GET.get('q', None)
	category_name = request.GET.get('c', None)
	if category_name:
		category = Category.objects.get(name__exact=category_name)
		videos = Video.objects.filter(category__exact=category, status__exact='public', processed__exact=True)
		context['category'] = category
	else:
		videos = Video.objects.filter(status__exact='public', processed__exact=True)
	if search:
		videos = videos.filter(title__icontains=search)
	context['videos'] = videos
	if request.user.is_authenticated:
		context['channel'] = Channel.objects.get(user__exact=request.user)
	return render(request, 'streamer/index.html', context)

def video(request, watch_id):
	video = get_object_or_404(Video, watch_id__exact=watch_id)
	video.view_count += 1
	video.save()
	like_count = Likes.objects.filter(video__exact=video).count()
	dislike_count = Dislikes.objects.filter(video__exact=video).count()
	is_video_liked = False
	is_video_disliked = False
	subscribed = False
	if request.user.is_authenticated:
		channel = Channel.objects.get(owner__exact=request.user)
		playlist = Playlist.objects.get(owner__exact=channel, title__exact='History')
		playlistEntry = PlaylistEntry.objects.create(video=video)
		playlist.videos.add(playlistEntry)
		is_video_liked = Likes.objects.filter(user__exact=request.user, video__exact=video).exists()
		is_video_disliked = Dislikes.objects.filter(user__exact=request.user, video__exact=video).exists()
		loggedin_channel = Channel.objects.get(owner__exact=request.user)
		subscribed = Subscription.objects.filter(from_channel__exact=loggedin_channel, to_channel__exact=channel).exists()
	formats = video.format_set.complete().all()
	recommended_videos = Video.objects.filter(status__exact='public', processed__exact=True)
	comments = Comment.objects.filter(active=True, parent__isnull=True, video__exact=video)
	return render(request, 'streamer/video.html', {'video' : video, 'formats' : formats, 'is_video_liked' : is_video_liked, 'is_video_disliked': is_video_disliked, 'like_count' : like_count, 'dislike_count' : dislike_count, 'subscribed' : subscribed, 'recommended_videos' : recommended_videos, 'comments' : comments})

@login_required
def uploadVideo(request):
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get('get_thumbnail'):
				video = Video.objects.get(watch_id__exact=request.POST.get('watch_id'))
				response = {'thumbnails' : []}
				for i in list(range(3)):
					timestamp = min(((video.duration / 3) / 0.5) + i, video.duration-0.5)
					tmp_thumbnail = FFmpegBackend().get_thumbnail(video_path=video.file.path, at_time=timestamp)
					filename = 'thumbnail_{}_{}.jpg'.format(video.watch_id, i)
					server_path = os.path.join(settings.MEDIA_ROOT, filename)
					shutil.move(tmp_thumbnail, server_path)
					url = settings.MEDIA_URL + filename
					response['thumbnails'].append(url)
				return JsonResponse(response)
			else:
				form = VideoForm(request.POST, request.FILES)
				if not request.FILES.get('file').content_type.startswith('video/'):
					return JsonResponse({'is_valid' : False})
				if form.is_valid():
					try:
						video = form.save()
					except FFmpegError as e:
						os.remove(os.path.join(settings.MEDIA_ROOT, form.files['file'].name))
						return JsonResponse({'is_valid' : False})
					video.channel = Channel.objects.get(owner__exact=request.user.id)
					video.status = 'drafting'
					video.save()

					logger.info('VALIDATING MIME-TYPE: {}'.format(video.file.path))
					f = os.path.join(settings.MEDIA_ROOT, video.file.name)
					if not magic.from_file(f, mime=True).startswith('video/'):
						logger.info('FILE INVALID: {}'.format(video.file.path))
						video.delete()
					else:
						logger.info('FILE VALID: {}'.format(video.file.path))

					try:
						Video.objects.get(pk=video.pk)
						data = {'is_valid' : True, 'name' : video.file.name, 'url' : video.file.url, 'watch_id' : video.watch_id}
					except Exception as e:
						data = {'is_valid' : False}
				else:
					data = {'is_valid' : False}
				return JsonResponse(data)
		else:
			video = Video.objects.get(watch_id__exact=request.POST.get('watch_id', ''))
			if request.POST.get('selected_thumbnail') == "custom":
				pass
			else:
				filename = os.path.basename(request.POST.get('selected_thumbnail'))
				full_path = os.path.join(settings.MEDIA_ROOT, filename)
				f = open(full_path, 'rb')
				video.thumbnail.save(filename, ImageFile(f), save=False)
				f.close()
				for i in range(3):
					name = '{}{}.jpg'.format(filename.split('.')[0][:-1], i)
					path = os.path.join(settings.MEDIA_ROOT, name)
					if os.path.isfile(path):
						os.remove(path)
			video.title = request.POST.get('title')
			video.description = request.POST.get('description')
			video.status = 'public'
			video.category = Category.objects.get(pk=request.POST.get('category'))
			video.save()
			logger.info('START CONVERTING' + video.file.path)
			enqueue(tasks.convert_all_videos,
					video._meta.app_label,
					video._meta.model_name,
					video.pk)
			return redirect("/")
	else:
		form = VideoForm()
		categories = Category.objects.all()
		return render(request, 'streamer/upload.html', {'form' : form, 'initial_upload' : True, 'categories' : categories})

@login_required
def editVideo(request, watch_id):
	video = get_object_or_404(Video, watch_id__exact=watch_id)
	if request.method == 'POST':
		form = EditVideoForm(request.POST, request.FILES or None, instance=video)
		if form.is_valid():
			form.save()
			return redirect('/dashboard')
	form = EditVideoForm(instance=video)
	return render(request, 'streamer/edit_video.html', {'form' : form, 'video' : video})

@login_required
def deleteVideo(request):
	if request.method == 'POST':
		video = Video.objects.get(watch_id__exact=request.POST.get('watch_id'))
		channel = Channel.objects.get(owner__exact=request.user)
		if video.channel == channel:
			video.delete()
			return JsonResponse({"success" : True})
		else:
			raise SuspiciousOperation
	else:
		raise SuspiciousOperation

def channel(request, channel_id):
	channel = Channel.objects.get(channel_id__exact=channel_id)
	videos = Video.objects.filter(channel__exact=channel, status__exact='public', processed__exact=True)

	if request.user.is_authenticated:
		loggedin_channel = Channel.objects.get(owner__exact=request.user)
		subscribed = Subscription.objects.filter(from_channel__exact=loggedin_channel, to_channel__exact=channel).exists()
	else:
		subscribed = False

	subscriber_count = Subscription.objects.filter(to_channel__exact=channel).count()
	view_count = 0
	for v in videos:
		view_count += v.view_count
	return render(request, 'streamer/channel.html', {'channel' : channel, 'videos' : videos, 'subscribed' : subscribed, 'subscriber_count' : subscriber_count, 'view_count' : view_count})

@login_required
def history(request):
	channel = Channel.objects.get(owner__exact=request.user.id)
	playlist = Playlist.objects.get(owner__exact=channel, title__exact='History')
	videos = playlist.videos.order_by('-date_added')
	return render(request, 'streamer/history.html', { 'videos' : videos })

def subscribe(request):
	if request.method == 'POST' and request.user.is_authenticated:
		from_channel = Channel.objects.get(owner__exact=request.user)
		to_channel = Channel.objects.get(pk=request.POST.get('channel_id'))

		if request.POST.get('action') == 'subscribe':
			Subscription.objects.create(from_channel=from_channel, to_channel=to_channel)
		else:
			subscription = Subscription.objects.get(from_channel__exact=from_channel, to_channel__exact=to_channel)
			subscription.delete()

		subscriber_count = Subscription.objects.filter(to_channel__exact=to_channel).count()
		return JsonResponse({'success' : True, 'subscriber_count' : subscriber_count})
	else:
		raise SuspiciousOperation

def like(request):
	if request.method == 'POST' and request.user.is_authenticated:
		video = Video.objects.get(pk=request.POST.get('video_id'))
		
		was_disliked = False
		if request.POST.get('action') == 'like':
			if not Likes.objects.filter(user__exact=request.user, video__exact=video).exists():
				was_disliked = Dislikes.objects.filter(user__exact=request.user, video__exact=video).delete()[0] > 0
				Likes.objects.create(video=video, user=request.user)
		
		elif request.POST.get('action') == 'unlike':
			Likes.objects.filter(user__exact=request.user, video__exact=video).delete()

		like_count = Likes.objects.filter(video__exact=video).count()
		dislike_count = Dislikes.objects.filter(video__exact=video).count()
		return JsonResponse({'success' : True, 'like_count' : like_count, 'dislike_count' : dislike_count, 'was_disliked' : was_disliked})
	else:
		raise SuspiciousOperation

def dislike(request):
	if request.method == 'POST' and request.user.is_authenticated:
		video = Video.objects.get(pk=request.POST.get('video_id'))

		was_liked = False
		if request.POST.get('action') == 'dislike':
			if not Dislikes.objects.filter(user__exact=request.user, video__exact=video).exists():
				was_liked = Likes.objects.filter(user__exact=request.user, video__exact=video).delete()[0] > 0
				Dislikes.objects.create(video=video, user=request.user)
		elif request.POST.get('action') == 'undislike':
			Dislikes.objects.filter(user__exact=request.user, video__exact=video).delete()

		like_count = Likes.objects.filter(video__exact=video).count()
		dislike_count = Dislikes.objects.filter(video__exact=video).count()
		return JsonResponse({'success' : True, 'like_count' : like_count, 'dislike_count' : dislike_count, 'was_liked' : was_liked})
	else:
		raise SuspiciousOperation

def comment(request):
	if request.method == 'POST' and request.user.is_authenticated:
		if request.POST.get('parent_id'):
			comment = Comment.objects.create(video=Video.objects.get(pk=request.POST.get('video_id')), user=request.user, text=request.POST.get('text'), parent=Comment.objects.get(pk=request.POST.get('parent_id')))
			html = """
			<div style="margin-left: 10px;" class="comment-container">
				<div class="comment-body">
					{text}
				</div>
				<div class="comment-meta">
					<div style="margin-right: 10px;"><a href="/channel/{channel_id}">{author}</a></div>
					<div>{created}</div>
				</div>
			</div>
			""".format(text=comment.text, channel_id=comment.user.channel.channel_id, author=comment.user.channel.name, created=comment.created)
		else:
			comment = Comment.objects.create(video=Video.objects.get(pk=request.POST.get('video_id')), user=request.user, text=request.POST.get('text'))
			html = """
			<div class="comment-thread">
				<div class="comment-container">
					<div class="comment-body">
						{text}
					</div>
					<div class="comment-meta">
						<div style="margin-right: 10px;"><a href="/channel/{channel_id}">{author}</a></div>
						<div>{created}</div>
					</div>
				</div>
			</div>
			""".format(text=comment.text, channel_id=comment.user.channel.channel_id, author=comment.user.channel.name, created=comment.created)
		return JsonResponse({'success' : True, 'comment' : html})
	else:
		raise SuspiciousOperation


@login_required
def dashboard(request):
	channel = Channel.objects.get(owner__exact=request.user)
	videos = Video.objects.filter(channel__exact=channel)
	return render(request, 'streamer/dashboard.html', {'videos' : videos})
