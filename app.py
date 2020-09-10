# -*- coding: utf-8 -*-
#Application Main

import AppBase
from views import main
import saver
import sys

class Main(AppBase.MaiｎBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		self.hMainView=main.MainView()
		self.saver = saver.Saver()
		self.hMainView.Show()
		if len(sys.argv) == 2:
			self.hMainView.urlEdit.SetValue(sys.argv[1])
			self.saver.start(sys.argv[1])
		return True

	def OnExit(self):
		if self.saver.pipeServer != None:
			self.saver.pipeServer.exit()
		if self.saver.pipeClient != None:
			self.saver.pipeClient.close()

		#戻り値は無視される
		return 0

