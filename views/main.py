# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import logging
import os
import sys
import wx
import re
import ctypes
import pywintypes

import constants
import errorCodes
import globalVars
import menuItemsStore

from logging import getLogger
import simpleDialog
from .base import *

from views import mkDialog


class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800,400),
			self.app.config.getint(self.identifier,"sizeY",600,300),
			self.app.config.getint(self.identifier,"positionX",50,0),
			self.app.config.getint(self.identifier,"positionY",50,0)
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.urlEdit, self.urlStatic = self.creator.inputbox(_("ユーザ名または録画URLを入力"), None, "", 0, 500)
		self.startButton = self.creator.button(_("録画開始"), self.events.start)
		self.downloadArchiveButton = self.creator.button(_("このユーザの録画ライブを全てダウンロード"), self.events.downloadArchive)
		self.statusEdit, self.statusStatic = self.creator.inputbox(_("状況"), None, "", wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_DONTWRAP, 500)

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hHelpMenu=wx.Menu()

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu,"versionInfo",_("バージョン情報(&V) ..."))

		#メニューバーの生成
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る

		#バージョン情報
		if selected==menuItemsStore.getRef("versionInfo"):
			simpleDialog.dialog(_("バージョン情報"), _("%(appName)s Version %(versionNumber)s.\nCopyright (C) %(year)s %(developerName)s") %{"appName": constants.APP_NAME, "versionNumber": constants.APP_VERSION, "year":constants.APP_COPYRIGHT_YEAR, "developerName": constants.APP_DEVELOPERS})

	def start(self, event):
		globalVars.app.saver.start(self.parent.urlEdit.GetValue())

	def downloadArchive(self, event):
		globalVars.app.saver.downloadArchive(self.parent.urlEdit.GetValue())
