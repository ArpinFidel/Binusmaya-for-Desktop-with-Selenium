# (TODO) try plyer and win10toast modules for tray notifications

import os

from lib.notifications import Notifications

from lib import browseractions
from lib import login
from lib import forum

def init():
	try:
		forum.load_data()
	except Exception as e:
		print('Cannot load forum cache', e)			

if __name__ == '__main__':
	init()
	
	runPath = os.path.dirname(os.path.abspath(__file__))

	with browseractions.initialise_browser(runPath) as (browser, _):
		login.login(browser)
		forum.fetch_data(browser)
		if Notifications.has_notification:
			Notifications.notify()

	input()