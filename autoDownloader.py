# -*- coding: utf-8 -*-
# auto downloader

import saver
import locale
import twitcasting.twitcasting
import sys

locale.setlocale(locale.LC_ALL, "ja-jp")

if len(sys.argv) == 2:
	user = sys.argv[1]
else:
	user = input("Type user name.")
movies = []

result = twitcasting.twitcasting.GetMoviesByUser(user)
while len(result) > 0:
	movies += list(result)
	result = twitcasting.twitcasting.GetMoviesByUser(user, 0, 20, result[-1]["id"])
	del result[0]

saverObject = saver.Saver()
for i in movies:
	if i["is_recorded"] == True:
		saverObject.start(i["link"])
print("Done!")
