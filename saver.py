# -*- coding:utf-8 -*-
# 録画処理モジュール

import pathlib
import subprocess
import twitcasting.twitcasting
import datetime
import requests
import re

class Saver:
	def getHlsUrl(self, userId):
		if "/movie/" in userId:
			self.movieInfo = twitcasting.twitcasting.GetMovieInfo(userId[userId.rfind("/") + 1:])
			response = requests.get("http://twitcasting.tv/%s" %(userId)).text
			start = re.search("https:\\\/\\\/dl\d\d\.twitcasting\.tv\\\/tc\.vod\\\/", response).start()
			end = response.find("\"", start)
			url = response[start:end]
			url = url.replace("\\/", "/")
			return url
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
		if "/" in userId:
			userId = userId[0:userId.find("/")]
		if url == False:
			return
		if ":" in userId:
			userId = userId.replace(":", "_")
		startTime = datetime.datetime.fromtimestamp(self.movieInfo["movie"]["created"])
		fileType = "mp3"
		outDir = pathlib.Path("output")
		createUserDir = True
		if createUserDir == True:
			outDir = outDir.joinpath(userId)
		outDir.mkdir(parents=True, exist_ok=True)
		fileName = "%s(%s)" %(userId, startTime.strftime("%Y年%m月%d日%H時%M分%S秒"))
		cmd = [
			"ffmpeg",
			"-i",
			url,
			"-f",
			fileType,
			"%s/%s.%s" %(outDir, fileName, fileType)
		]
		subprocess.run(cmd)
