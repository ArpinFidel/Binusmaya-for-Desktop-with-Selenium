from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class initialise_browser:
	
	def __init__(self, runPath):
		self.runPath = runPath
	
	def __enter__(self):
		self.downloadPath = self.runPath+'\\lib\\downloads'
		self.browserPath = self.runPath+'\\lib\\chromedriver.exe'
		
		op = webdriver.ChromeOptions()
		prefs = {	'profile.default_content_setting_values': {
						# 'cookies': 2,
						'images': 2,
						'plugins': 2,
						'popups': 2,
						'geolocation': 2, 
						'notifications': 2,
						'auto_select_certificate': 2,
						'fullscreen': 2, 
						'mouselock': 2,
						'mixed_script': 2,
						'media_stream': 2, 
						'media_stream_mic': 2,
						'media_stream_camera': 2,
						'protocol_handlers': 2, 
						'ppapi_broker': 2,
						'automatic_downloads': 2,
						'midi_sysex': 2, 
						'push_messaging': 2,
						'ssl_cert_decisions': 2,
						'metro_switch_to_desktop': 2, 
						'protected_media_identifier': 2,
						'app_banner': 2,
						'site_engagement': 2, 
						'durable_storage': 2},
					'disk-cache-size': 4096,
					'download.default_directory': self.downloadPath
				}

		args = [
				# 'headless',
				'--silent',
				'--disable-gpu',
				'--disable-notifications',
				'--log-level=1',
				'--disable-extensions',
				'test-type'
				]

		sargs = [
			'hide_console'
			]
		
		for arg in args:
			op.add_argument(arg)
			
		op.add_experimental_option("prefs", prefs)
		
		self.browser = webdriver.Chrome(self.browserPath, options=op, service_args=sargs)

		self.browser.implicitly_wait(5)
		
		return self.browser, self.downloadPath
	
	def __exit__(self, type, value, traceback):
		self.browser.quit()

def stop_loading(browser):
	sleep(1)
	browser.find_element(By.TAG_NAME, "body").send_keys("Keys.ESCAPE")

def remove_non_path(path):
	for c in r'\/:*?"<>|':
		path=path.replace(c, '')
	return path
