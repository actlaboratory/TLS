# -*- coding:utf-8 -*-
# 録画処理モジュール

import os
import subprocess
import twitcasting.twitcasting
import datetime

class Saver:
	def getHlsUrl(self, userId):
		self.movieInfo = twitcasting.twitcasting.GetCurrentLive(userId)
		try:
			return self.movieInfo["movie"]["hls_url"]
		except KeyError:
			return False

	def start(self, userId):
		url = self.getHlsUrl(userId)
		if url == False:
			return
		startTime = datetime.datetime.fromtimestamp(self.movieInfo["movie"]["created"])
		startTime = startTime.strftime("%Y%m%d_%H%M%S")
		file = "output/%s_%s.mp4" %(userId, startTime)
		if ":" in file:
			file = file.replace(":", "_")
		cmd = [
			"ffmpeg",
			"-i",
			url,
			"-c",
			"copy",
			file
		]
		subprocess.run(cmd)
