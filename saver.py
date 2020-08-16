# -*- coding:utf-8 -*-
# 録画処理モジュール

import pathlib
import subprocess
import twitcasting.twitcasting
import datetime
import requests
import re
import globalVars
import wx
import simpleDialog
import winsound

getStatus = 0
getCurrentLive = 1
archive = 2
realtime = 3

class Saver:
	def __init__(self):
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)

	def getHlsUrl(self, userId):
		if "/movie/" in userId:
			self.mode = archive
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
		self.mode = realtime
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
			return False
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
		target = pathlib.Path("%s/%s.%s" %(outDir, fileName, fileType))
		if target.exists() == True:
			question = simpleDialog.yesNoDialog(_("確認"), _("%sはすでに存在します。上書きしてもよろしいですか？") %target.as_posix())
			if question == wx.ID_NO:
				return
		cmd = [
			"ffmpeg",
			"-y",
			"-i",
			url,
			"-f",
			fileType,
			target.as_posix()
		]
		self.result = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, encoding="utf-8")
		globalVars.app.hMainView.urlEdit.Clear()
		globalVars.app.hMainView.statusEdit.Clear()
		self.getStatusTimer = wx.Timer(self.evtHandler, getStatus)
		self.getStatusTimer.Start(1000)

	def getStatus(self):
		cursorPoint = globalVars.app.hMainView.statusEdit.GetInsertionPoint()
		globalVars.app.hMainView.statusEdit.SetValue(globalVars.app.hMainView.statusEdit.GetValue() + self.result.stdout.readline())
		globalVars.app.hMainView.statusEdit.SetInsertionPoint(cursorPoint)

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == getStatus:
			self.getStatus()
			if self.result.poll() != None:
				timer.Stop()
				checkNextLive = True
				if self.mode == realtime and checkNextLive == True:
					self.checkNextLive()
					return
				self.end()
		elif id == getCurrentLive:
			self.count += 1
			currentLive = self.getHlsUrl(self.userId)
			if currentLive != False:
				timer.Stop()
				self.start(self.userId)
			elif currentLive == False and self.count == 100:
				timer.Stop()
				self.end()

	def end(self):
		autoClose = True
		if autoClose == True:
			globalVars.app.hMainView.events.Exit()

	def checkNextLive(self):
		self.userId = self.movieInfo["broadcaster"]["id"]
		self.getCurrentLiveTimer = wx.Timer(self.evtHandler, getCurrentLive)
		self.count = 0
		self.getCurrentLiveTimer.Start(5000)
