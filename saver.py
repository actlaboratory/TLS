# -*- coding:utf-8 -*-
# 録画処理モジュール

import os
import subprocess
import twitcasting.twitcasting
import datetime

class Saver:
	def getHlsUrl(self, userId):
		try:
			return twitcasting.twitcasting.GetCurrentLive(userId)["movie"]["hls_url"]
		except KeyError:
			return False

	def start(self, userId):
		url = self.getHlsUrl(userId)
		if url == False:
			return
		now = datetime.datetime.now()
		now = now.strftime("%Y%m%d_%H%M%S")
		file = "output/%s_%s.mp4" %(userId, now)
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
