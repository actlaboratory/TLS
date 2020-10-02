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
import constants
import views.password
import pickle
import os
import namedPipe.server

getStatus = 0
getCurrentLive = 1
archive = 2
realtime = 3
comment = 4

class Saver:
	def __init__(self):
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)
		self.changeView(False)
		self.pipeServer = None
		self.pipeClient = None

	def getHlsUrl(self, userId):
		if "/movie/" in userId:
			self.mode = archive
			self.movieInfo = twitcasting.twitcasting.GetMovieInfo(userId[userId.rfind("/") + 1:])
			session = requests.session()
			try:
				response = session.get(self.movieInfo["movie"]["link"])
			except:
				return False
			if self.movieInfo["movie"]["is_protected"] == True:
				dialog = views.password.Dialog()
				dialog.Initialize()
				ret = dialog.Show()
				if ret == wx.ID_CANCEL:
					return
				password = dialog.GetData()
				response = session.post(self.movieInfo["movie"]["link"], data="password=%s" %password, headers={"Content-Type": "application/x-www-form-urlencoded"})
			response = response.text
			try:
				start = re.search("https:\\\/\\\/dl\d\d\.twitcasting\.tv\\\/tc\.vod\\\/", response).start()
			except:
				return False
			end = response.find("\"", start)
			url = response[start:end]
			url = url.replace("\\/", "/")
			return url
		self.mode = realtime
		self.movieInfo = twitcasting.twitcasting.GetCurrentLive(userId)
		try:
			self.userId = self.movieInfo["broadcaster"]["id"]
			return self.movieInfo["movie"]["hls_url"]
		except KeyError:
			try:
				self.userId = twitcasting.twitcasting.GetUserInfo(userId)["user"]["id"]
			except:
				return False

	def start(self, userId, noexit=False):
		userId = userId.replace("http://twitcasting.tv/", "")
		userId = userId.replace("https://twitcasting.tv/", "")
		if "/" in userId:
			userId = userId[0:userId.find("/")]
		url = self.getHlsUrl(userId)
		if url == False:
			simpleDialog.errorDialog(_("録画に失敗しました。録画ライブの指定が間違っているか、現在放送中ではありません。"))
			return
		self.changeView(True)
		if url == None:
			if self.mode == archive:
				self.changeView(False)
				return
			waitLiveStart = globalVars.app.config.getboolean("recording", "waitLiveStart", True)
			if waitLiveStart == True:
				self.changeTitle(_("ライブ開始待機中:%s") %userId)
				self.checkNextLive()
			else:
				simpleDialog.errorDialog(_("このユーザは現在配信中ではありません。"))
			return
		if "/" in userId:
			userId = userId[0:userId.find("/")]
		if ":" in userId:
			userId = userId.replace(":", "-")
		startTime = datetime.datetime.fromtimestamp(self.movieInfo["movie"]["created"])
		fileType = globalVars.app.config["recording"]["fileType"]
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
		outDir = pathlib.Path(globalVars.app.config["recording"]["outDir"])
		createSubDir = globalVars.app.config.getboolean("recording", "createSubDir", True)
		if createSubDir == True:
			subDirName = globalVars.app.config["recording"]["subDirName"]
			for i, j in nameReplaceList.items():
				subDirName = subDirName.replace(i, j)
			outDir = outDir.joinpath(subDirName)
		outDir.mkdir(parents=True, exist_ok=True)
		fileName = globalVars.app.config["recording"]["fileName"]
		for i, j in nameReplaceList.items():
			fileName = fileName.replace(i, j)
		movieId = self.movieInfo["movie"]["id"]
		target = pathlib.Path("%s/%s.%s" %(outDir, fileName, fileType))
		if target.exists() == True:
			num = 1
			while target.exists():
				num += 1
				name = fileName + " (%i)" %num
				target = pathlib.Path("%s/%s.%s" %(outDir, name, fileType))
		getComment = globalVars.app.config.getboolean("recording", "getComment", False)
		if getComment == True:
			self.commentFile = pathlib.Path("%s/%s.txt" %(outDir, fileName))
			self.commentFile.touch()
			self.getCommentTimer = wx.Timer(self.evtHandler, comment)
			self.getCommentTimer.Start(5000)
			self.comments = []
			self.lastCommentId = ""
		cmd = [
			"ffmpeg",
			"-y",
			"-i",
			url,
			"-f",
			fileType,
			target.as_posix()
		]
		self.changeTitle(_("録画中:%s") %self.movieInfo["broadcaster"]["screen_id"])
		self.isRunning = True
		if self.pipeServer == None:
			self.pipeServer = namedPipe.server.Server("ffmpeg_msg")
			self.pipeServer.setReceiveCallback(self.getStatus)
			self.pipeServer.start()
		if self.pipeClient == None:
			self.pipeClient = open("\\\\.\\pipe\\ffmpeg_msg", "wb")
		self.result = subprocess.Popen(cmd, stdout = self.pipeClient, stderr = subprocess.STDOUT, encoding="utf-8")
		globalVars.app.hMainView.urlEdit.Clear()
		globalVars.app.hMainView.statusEdit.Clear()
		while True:
			wx.YieldIfNeeded()
			if self.result.poll() != None:
				break
		checkNextLive = globalVars.app.config.getboolean("recording", "checkNextLive", True)
		self.isRunning = False
		if self.mode == realtime and checkNextLive == True:
			self.changeTitle(_("待機中:%s") %self.movieInfo["broadcaster"]["screen_id"])
			self.checkNextLive()
			return
		if noexit == False:
			self.end()
		return True

	def getStatus(self, msg):
		cursorPoint = globalVars.app.hMainView.statusEdit.GetInsertionPoint()
		globalVars.app.hMainView.statusEdit.SetValue(globalVars.app.hMainView.statusEdit.GetValue() + msg)
		globalVars.app.hMainView.statusEdit.SetInsertionPoint(cursorPoint)

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == getCurrentLive:
			self.count += 1
			currentLive = self.getHlsUrl(self.userId)
			if currentLive != False and currentLive != None:
				timer.Stop()
				self.start(self.userId)
			elif self.count == 20:
				timer.Stop()
				self.end()
		elif id == comment:
			if self.isRunning == False:
				timer.Stop()
				return
			self.getComment()

	def end(self):
		autoClose = globalVars.app.config.getboolean("recording", "autoClose", True)
		if autoClose == True:
			globalVars.app.hMainView.events.Exit()
			return
		self.changeTitle(_("録画終了"))

	def checkNextLive(self):
		self.count = 0
		self.getCurrentLiveTimer = wx.Timer(self.evtHandler, getCurrentLive)
		self.getCurrentLiveTimer.Start(30000)

	def changeTitle(self, string = ""):
		if string == "":
			globalVars.app.hMainView.hFrame.SetTitle(constants.APP_NAME)
			return
		globalVars.app.hMainView.hFrame.SetTitle("%s - %s" %(string, constants.APP_NAME))

	def getComment(self):
		result = twitcasting.twitcasting.GetComments(self.movieInfo["movie"]["id"], 0, 50, self.lastCommentId)
		if len(result) == 0 or type(result) != list:
			return
		result.reverse()
		self.lastCommentId = result[-1]["id"]
		for i in result:
			tmp = [
				i["from_user"]["name"],
				i["message"],
				datetime.datetime.fromtimestamp(i["created"]).strftime("%Y/%m/%d %H:%M:%S"),
				i["from_user"]["screen_id"]
			]
			tmp = "\t".join(tmp)
			self.comments.append(tmp)
		self.commentFile.write_text("\n".join(self.comments), encoding="utf-8")

	def downloadArchive(self, user):
		user = user.replace("http://twitcasting.tv/", "")
		user = user.replace("https://twitcasting.tv/", "")
		if "/" in user:
			user = user[0:user.find("/")]
		movies = []
		result = twitcasting.twitcasting.GetMoviesByUser(user)
		while len(result) > 0:
			movies += list(result)
			result = twitcasting.twitcasting.GetMoviesByUser(user, 0, 20, result[-1]["id"])
			del result[0]
		done = 0
		for i in movies:
			if i["is_recorded"] == True:
				result = self.start(i["link"], True)
				if result == True:
					done += 1
		simpleDialog.dialog(_("完了"), _("%i個のライブをダウンロードしました。") %done)
		self.end()

	def changeView(self, mode):
		if mode == True:
			globalVars.app.hMainView.urlEdit.Disable()
			globalVars.app.hMainView.startButton.Disable()
			globalVars.app.hMainView.downloadArchiveButton.Disable()
			globalVars.app.hMainView.statusEdit.Enable()
			globalVars.app.hMainView.statusEdit.SetFocus()
		elif mode == False:
			globalVars.app.hMainView.urlEdit.Enable()
			globalVars.app.hMainView.startButton.Enable()
			globalVars.app.hMainView.downloadArchiveButton.Enable()
			globalVars.app.hMainView.statusEdit.Disable()
			globalVars.app.hMainView.urlEdit.SetFocus()

	