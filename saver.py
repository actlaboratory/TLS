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
		if "https://twitcasting.tv/" in userId:
			userId = userId[23:]
		elif "http://twitcasting.tv/" in userId:
			userId = userId[22:]
		url = self.getHlsUrl(userId)
		if url == False:
			return
		startTime = datetime.datetime.fromtimestamp(self.movieInfo["movie"]["created"])
		startTime = startTime.strftime("%Y%m%d_%H%M%S")
		extension = "mp4"
		file = "output/%s_%s.%s" %(userId, startTime, extension)
		if ":" in file:
			file = file.replace(":", "_")
		cmd = [
			"ffmpeg",
			"-i",
			url,
			"-f",
			extension,
			file
		]
		subprocess.run(cmd)
