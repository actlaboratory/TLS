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
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。


		#戻り値は無視される
		return 0

