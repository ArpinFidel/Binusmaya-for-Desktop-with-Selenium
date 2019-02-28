from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from lib import silence
from time import sleep
from getpass import getpass

import contextlib
import pathlib
import os

# login constants
login_url='https://binusmaya.binus.ac.id/login/'
	
username_field_xpath='//*[@id="login"]/form/div[1]/label/input'
password_field_xpath='//*[@id="login"]/form/p[1]/span/input'
login_button_css='.button.button-primary.wide'

# forum constants
forum_url='https://binusmaya.binus.ac.id/newStudent/#/forum/class'
	
period_field_xpath='//*[@id="ddlPeriod"]'
periods_xpath='//*[@id="ddlPeriod"]/option'

course_field_xpath='//*[@id="ddlCourse"]'
courses_xpath='//*[@id="ddlCourse"]/option'

class_field_xpath='//*[@id="ddlClass"]'
classs_xpath='//*[@id="ddlClass"]/option'

threads_xpath='//*[@id="threadtable"]/tbody/tr'

no_thread_html='<td colspan="4" style="text-align:center;">No Data Found</td>'

thread_title_class='ctitle'

class Notifications:
	forum=[]
	has_notification=False

	def __init__(self):
		pass

	@staticmethod
	def add_forum_notification(notification):
		Notifications.forum.append(notification)
		Notifications.has_notification=True
	
	# (TODO) change to actual notifications later
	@staticmethod
	def notify():
		if Notifications.forum:
			print('Forum:')
			for f in Notifications.forum:
				print(f)
			print('=======================')
		
		Notifications.forum=[]
		Notifications.has_notification=False

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

		self.browser.implicitly_wait(20)
		
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

class Login:
	def __init__(self):
		pass
	
	@staticmethod
	def get_credentials():
		filepath='.\\lib\\credentials.txt'
		try:
			with open(filepath, 'r') as cred_file:
				username, password=cred_file.read().splitlines()[:2]
				
		except:
			username=input('Username: ')
			password=getpass('Password: ')
			
			remember=input('Remember password? Your password will be saved as plaintext. [y/N]: ')
			
			if (remember.lower() in ('y', 'yes')):
				with open(filepath, 'w') as cred_file:
					cred_file.write(username + '\n')
					cred_file.write(password + '\n')
			
		return username, password
		
	@staticmethod
	def is_logged_in(browser):
		user_name_xpath='//*[@id="aUsername"]'
		try:
			browser.find_element(By.XPATH, user_name_xpath)
		except:
			return False
		else:
			return True
	
	@staticmethod
	def find_login_elements(browser):
		exceptions=set()
		for _ in range(5):
			try:
				elements=(
					browser.find_element(By.XPATH, username_field_xpath)
					, browser.find_element(By.XPATH, password_field_xpath)
					, browser.find_element(By.CSS_SELECTOR, login_button_css)
					)
				break
			except Exception as e:
				exceptions.add(e)
				sleep(0.5)	
		else: raise Exception(TimeoutError('Cannot find login fields'), exceptions)
		
		return elements
	
	
	@staticmethod
	def login(browser):
		
		print('Logging in')
		login_exceptions=set()
		for _ in range(10):
			try:
				print('Getting credentials')
				username, password = Login.get_credentials()
				
				browser.get(login_url)
				
				print('Trying to find login fields')
				username_field, password_field, login_button=Login.find_login_elements(browser)
				
				print('Entering credentials')
				username_field.send_keys(username)
				password_field.send_keys(password)
				login_button.click()
				
				sleep(0.25)
				if Login.is_logged_in(browser): break
			except Exception as e:
				login_exceptions.add(e)
				sleep(0.5)
			else:
				sleep(0.5)
				if not Login.is_logged_in(browser): login_exceptions.add(Exception('Server is not responding'))
		else: raise Exception(TimeoutError('Cannot login'), login_exceptions)
		
		print('Stopping browser from redirecting')
		stop_loading(browser)
		
		print('Finished login')

	@staticmethod
	def handle_session_timeout(browser):
		try:
			browser.switch_to.alert.accept()
		except:
			if Login.is_logged_in(browser): return
			
		stop_loading(browser)
		Login.login(browser)

def load_url(browser, url):
	for _ in range(20):
		if browser.current_url == url: break
		browser.get(url)
		if Login.is_logged_in(browser): break
		Login.handle_session_timeout(browser)
		sleep(0.5)

class Forum:
	periods={}
	
	def __init__(self):
		pass
	
	class Period:
		def __init__(self, idx, name):
			self.idx = idx
			self.name = name
			self.courses = {}

		def path(self):
			return remove_non_path(self.name)
	
	class Course:
		def __init__(self, idx, name):
			self.idx = idx
			self.name = name
			self.classes = {}
	
		def path(self):
			return remove_non_path(self.name)
	
	class Class:
		def __init__(self, idx, name):
			self.idx = idx
			self.name = name
			self.threads = set()
			
		def path(self):
			return remove_non_path(self.name)
	
	class Thread:
		def __init__(self, url, name, by):
			self.url = url
			self.name = name
			self.by = by
			if url[-5:] != '?id=1': raise ValueError('Unexpected url suffix')
		
		def path(self):
			return remove_non_path(self.name)
	
		def get_idx(self):
			return self.url.split('.')[-1][:-5]
	
	@staticmethod
	def find_forum_fields(browser):
		exceptions=set()
		for _ in range(10):
			try:
				fields=(Select(browser.find_element(By.XPATH, period_field_xpath))
					, Select(browser.find_element(By.XPATH, course_field_xpath))
					, Select(browser.find_element(By.XPATH, class_field_xpath)))
				break
			except Exception as e:
				exceptions.add(e)
				sleep(1)
		else: raise Exception(TimeoutError('Unable to find forum fields'), exceptions)
		
		return fields
	
	@staticmethod
	def find_periods(browser):
		exceptions=set()
		for _ in range(10):
			try:
				periods=browser.find_elements(By.XPATH, periods_xpath)
				break
			except Exception as e:
				exceptions.add(e)
				sleep(1)
		else: raise Exception(TimeoutError('Unable to retrieve available periods'), periods)
		
		return [Forum.Period(p.get_attribute('value'), p.get_attribute('innerHTML')) for p in periods]
	
	@staticmethod
	def find_courses(browser):
		exceptions=set()
		for _ in range(5):
			try:
				courses=browser.find_elements(By.XPATH, courses_xpath)
				break
			except Exception as e:
				exceptions.add(e)
				sleep(0.5)
		else: raise Exception(TimeoutError('Unable to retrieve available courses', exceptions))
		
		return [Forum.Course(c.get_attribute('value'), c.get_attribute('innerHTML')) for c in courses]

	@staticmethod
	def find_classes(browser):
		exceptions=set()
		for _ in range(5):
			try:
				classes=browser.find_elements(By.XPATH, classs_xpath)
				break
			except Exception as e:
				exceptions.add(e)
				sleep(0.5)
		else: raise Exception(TimeoutError('Unable to retrieve available classes', exceptions))
		
		return [Forum.Class(c.get_attribute('value'), c.get_attribute('innerHTML')) for c in classes]

	@staticmethod
	def get_threads(browser):
		exceptions=set()
		for _ in range(5):
			try:
				threads=browser.find_elements(By.XPATH, threads_xpath)
				break
			except Exception as e:
				exceptions.add(e)
				sleep(1)
		else: raise Exception(TimeoutError('Unable to retrieve threads', exceptions))

		if threads and (no_thread_html in (t.get_attribute('innerHTML') for t in threads)):
			return set()
		
		threads=[t.find_element(By.CLASS_NAME, thread_title_class) for t in threads]
		threads=[Forum.Thread(t.find_element(By.TAG_NAME, 'a').get_attribute('href')
								, t.find_element(By.TAG_NAME, 'a').get_attribute('innerHTML')
								, t.get_attribute('innerHTML').split('By: ')[-1].strip()
								)
					for t in threads
				]
		
		return set(threads)

	# (TODO) salah total
	@staticmethod
	def load_cache():
		for period in Forum.periods:
			for course in period.courses:
				for clas in course.classes:
					path='forum/'+period.path()+'/'+course.path()+'/'+clas.path()

					with open(path+'/threads.txt', 'r+') as list_file:
						thread_names=set(t.strip() for t in list_file.readlines())
					
					for thread_name in thread_names:
						with open(path+thread_name, 'r+') as thread:
							properties=[t.strip() for t in thread.readlines()]
							clas.threads.add(Forum.Thread(properties[0], properties[1], properties[2]))
	@staticmethod
	def add_to_cache(period, course, clas, thread):
		path='forum/'+period.path()+'/'+course.path()+'/'+clas.path()

		pathlib.Path(os.getcwd()+'/'+path).mkdir(parents=True, exist_ok=True)

		with open(path+'/threads.txt', 'a+') as list_file:
			list_file.write(thread.name+'\n')
			
		with open(path+'/'+thread.path(), 'w+') as thread_file:
			thread_file.write(thread.url+'\n'+thread.name+'\n'+thread.by)

	@staticmethod
	def validate_cache():
		for period in Forum.periods:
			for course in period.courses:
				for clas in course.classes:
					if not clas.threads: continue
					
					path='forum/'+period.path()+'/'+course.path()+'/'+clas.path()

					with open(path+'/threads.txt', 'r+') as list_file:
						thread_names=[t.strip() for t in list_file.readlines()]
						thread_names_unique=set(thread_names)
					if len(thread_names) != len(thread_names_unique):
						with open(path+'/threads.txt', 'w+') as list_file:
							for thread_name in thread_names_unique:
								list_file.write(thread_name+'\n')

	@staticmethod
	def get_forum_data(browser):
		
		# load the page
		print('Loading forum')
		load_url(browser, forum_url)
		
		# wait for page to render
		print('Wating for page to render')
		sleep(3)
		
		# get fields
		print('Getting forum fields')
		period_field, course_field, class_field=Forum.find_forum_fields(browser)
		
		# get available periods
		print('Getting all available periods')
		Forum.periods=Forum.find_periods(browser)

		# get data for each period
		for period in Forum.periods:
			
			# select period in dropdown
			period_field.select_by_value(period.idx)

			# get available courses for the period
			print('Getting courses for', period.name)
			period.courses=Forum.find_courses(browser)
			
			# get data for each course
			for course in period.courses:
				
				# select course in dropdown
				course_field.select_by_value(course.idx)
			
				# get available classes for each course
				print('Getting classes for', course.name)
				course.classes=Forum.find_classes(browser)
				
				# get data for each class
				for clas in course.classes:
					
					# select course in dropdown
					class_field.select_by_value(clas.idx)
					
					# get threads for the class
					print('Getting threads for', course.name, clas.name)
					threads=Forum.get_threads(browser)

					# check for new threads
					for thread in threads:
						if thread not in clas.threads:
							# add new thread to notifications
							Notifications.add_forum_notification('New thread by '+thread.by+': '+thread.name)
							# add thread to database
							Forum.add_to_cache(period, course, clas, thread)

					clas.threads=threads

					# (TODO) delete later
					for thread in threads:
						print(thread.name, thread.by, thread.url, thread.get_idx(), '\n', sep='\n')
				
				print('===============================')
			Forum.validate_cache()

if __name__ == '__main__':
	
	Forum.load_cache()

	runPath = os.path.dirname(os.path.abspath(__file__))

	with initialise_browser(runPath) as (browser, _):
		Login.login(browser)
		Forum.get_forum_data(browser)
		if Notifications.has_notification:
			Notifications.notify()

	input()