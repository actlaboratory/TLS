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
			session = requests.session()
			response = session.get(self.movieInfo["movie"]["link"])
			if self.movieInfo["movie"]["is_protected"] == True:
				password = input("Type password.")
				response = session.post(self.movieInfo["movie"]["link"], data="password=%s" %password, headers={"Content-Type": "application/x-www-form-urlencoded"})
				response = response.text
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
			userId = userId.replace(":", "-")
		startTime = datetime.datetime.fromtimestamp(self.movieInfo["movie"]["created"])
		fileType = "mp3"
		nameReplaceList = {
			"%user_id%": self.movieInfo["broadcaster"]["id"],
			"%user_screen_id%": self.movieInfo["broadcaster"]["screen_id"],
			"%user_name%": self.movieInfo["broadcaster"]["name"],
			"%year%": startTime.strftime("%Y"),
			"%month%": startTime.strftime("%m"),
			"%day%": startTime.strftime("%d"),
			"%hour%": startTime.strftime("%H"),
			"%minute%": startTime.strftime("%M"),
			"%second%": startTime.strftime("%S"),
			"%movie_title%": self.movieInfo["movie"]["title"],
			"%movie_id%": self.movieInfo["movie"]["id"]
		}
		outDir = pathlib.Path("output")
		createSubDir = True
		if createSubDir == True:
			subDirName = "%user_screen_id%"
			for i, j in nameReplaceList.items():
				subDirName = subDirName.replace(i, j)
			outDir = outDir.joinpath(subDirName)
		outDir.mkdir(parents=True, exist_ok=True)
		fileName = "%user_screen_id%(%year%年%month%月%day%日%hour%時%minute%分%second%秒)"
		for i, j in nameReplaceList.items():
			fileName = fileName.replace(i, j)
		cmd = [
			"ffmpeg",
			"-i",
			url,
			"-f",
			fileType,
			"%s/%s.%s" %(outDir, fileName, fileType)
		]
		subprocess.run(cmd)
