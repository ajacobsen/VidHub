#!/usr/bin/env python3

import os

from django.core.management.base import BaseCommand, CommandError
from streamer.models import Video, VideoFile

class Command(BaseCommand):
	help = 'Find and delete stray files in media/'

	def handle(self, *args, **kwargs):
		self.stdout.write('Search for stray files...')
		curdir = os.path.abspath(os.path.curdir)
		videos = Video.objects.all()
		dbfiles = set()
		for video in videos:
			if video.file:
				dbfiles.add(video.file.file.path)
			if video.thumbnail:
				dbfiles.add(video.thumbnail.path)
			for vidformat in video.file.format_set.all():
				if vidformat.file:
					dbfiles.add(vidformat.file.path)

		realfiles = set()
		for dirname, dirnames, filenames in os.walk(os.path.join(curdir, 'media')):
			for filename in filenames:
				realfiles.add(os.path.join(curdir, dirname, filename))

		strayfiles = realfiles - dbfiles
		if not strayfiles:
			self.stdout.write('No stray files found!')
		for line in strayfiles:
			self.stdout.write('DELETING: {}'.format(line))
			# os.remove(line)

