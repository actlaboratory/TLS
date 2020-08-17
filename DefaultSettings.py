# -*- coding: utf-8 -*-
#default config

from ConfigManager import *


class DefaultSettings:
	def get():
		config = ConfigManager()
		config["general"]={
			"language": "ja-JP",
			"fileVersion": "100",
			"locale": "ja-JP"
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":"normal"
		}
		config["speech"]={
			"reader" : "AUTO"
		}
		config["mainView"]={
			"sizeX": "800",
			"sizeY": "600",
		}
		config["recording"]={
			"outDir": "output",
			"fileType": "mp4",
			"fileName": "$user_screen_id（$year年$month月$day日$hour時$minute分$second秒）",
			"createSubDir": True,
			"subDirName": "$user_screen_id",
			"waitLiveStart": True,
			"checkNextLive": True
		}
		return config
