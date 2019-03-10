# (TODO) try plyer and win10toast modules for tray notifications

from time import sleep
from getpass import getpass

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import os

from lib import silence
from lib import browseractions
from lib import login
from lib import forum

from lib.notifications import Notifications


def init():
	try:
		Forum.load_data()
	except:
		print('Forum cache not found')			

if __name__ == '__main__':
	init()

	runPath = os.path.dirname(os.path.abspath(__file__))

	with browseractions.initialise_browser(runPath) as (browser, _):
		login.login(browser)
		forum.fetch_data(browser)
		if Notifications.has_notification:
			Notifications.notify()

	input()