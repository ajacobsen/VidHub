import random
import string
import os
import logging

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from video_encoding.tasks import video_convert_done
from video_encoding.models import Format

from .models import Video


logger = logging.getLogger('django')

@receiver(post_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
	logger.info('CLEANING UP: {}'.format(instance.file.path))
	if instance.file:
		logger.info('DELETING: ' + instance.file.path)
		if os.path.isfile(instance.file.path):
			os.remove(instance.file.path)
	if instance.thumbnail:
		logger.info('DELETING: ' + instance.thumbnail.path)
		if os.path.isfile(instance.thumbnail.path):
			os.remove(instance.thumbnail.path)

@receiver(post_delete, sender=Format)
def delete_transcoded_video_files(sender, instance, **kwargs):
	if instance.file:
		logger.info('DELETING: ' + instance.file.path)
		if os.path.isfile(instance.file.path):
			os.remove(instance.file.path)

def generate_id(length):
	chars = string.ascii_letters + string.digits
	return ''.join(random.choice(chars) for _ in range(length))

@receiver(pre_save, sender=Video)
def pre_save_create_watch_id(sender, instance, **kwargs):
	if not instance.watch_id:
		new_watch_id = generate_id(8)
		while sender.objects.filter(watch_id=new_watch_id).exists():
			new_watch_id = generate_id(8)
		instance.watch_id = new_watch_id

@receiver(video_convert_done)
def on_video_convert_done(video, **kwargs):
	logger.info('VIDEO CONVERT DONE: {} {}'.format(video.file.name, video.watch_id))
	video.processed = True
	video.save()