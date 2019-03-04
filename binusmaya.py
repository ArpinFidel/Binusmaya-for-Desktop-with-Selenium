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

class Category:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return self.name==other.name
	
	def __ne__(self, other):
		return self.name!=other.name

	def __hash__(self):
		return hash(self.name)

	def path(self):
		return remove_non_path(self.name)

class Period(Category):
	def __init__(self, name):
		super().__init__(name)
		self.courses = {}
	
class Course(Category):
	def __init__(self, name):
		super().__init__(name)
		self.classes = {}

class Class(Category):
	def __init__(self, name):
		super().__init__(name)
		self.threads = set()
		
class Thread:
	def __init__(self, url, name, by):
		self.url = url
		self.name = name
		self.by = by
		if url[-5:] != '?id=1': raise ValueError('Unexpected url suffix')

	def get_idx(self):
		return self.url.split('.')[-1][:-5]
	
	def path(self):
		return remove_non_path(self.get_idx())

class Forum:
	periods={}
	
	def __init__(self):
		pass

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
		
		return [Period(p.get_attribute('innerHTML')) for p in periods]
	
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
		
		return [Course(c.get_attribute('innerHTML')) for c in courses]

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
		
		return [Class(c.get_attribute('innerHTML')) for c in classes]

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
		threads=[Thread(t.find_element(By.TAG_NAME, 'a').get_attribute('href')
								, t.find_element(By.TAG_NAME, 'a').get_attribute('innerHTML')
								, t.get_attribute('innerHTML').split('By: ')[-1].strip()
								)
					for t in threads
				]
		
		return set(threads)

	@staticmethod
	def load_cache():
		# read available periods
		with open('forum/periods.txt', 'r+') as periods_file:
			period_names=[line.strip() for line in periods_file.readlines()]

		# for each periods
		for period_name in period_names:
			period_path='forum/'+remove_non_path(period_name)

			# read data for the period
			with open(period_path+'/period.txt', 'r+') as period_file:
				period_data=[line.strip() for line in period_file.readlines()]

			# read available courses for the period
			with open(period_path+'/courses.txt', 'r+') as courses_file:
				course_names=[line.strip() for line in courses_file.readlines()]

			# save the period
			period=Period(period_data[0])
			Forum.periods[period.name]=period

			# for each course in the period
			for course_name in course_names:
				course_path=period_path+'/'+remove_non_path(course_name)

				# read data for the course
				with open(course_path+'/course.txt', 'r+') as course_file:
					course_data=[line.strip() for line in course_file.readlines()]

				# read available classes for the course
				with open(course_path+'/classes.txt', 'r+') as classes_file:
					class_names=[line.strip() for line in classes_file.readlines()]

				# save the course
				course=Course(course_data[0])
				period.courses[course.name]=course
				
				# for each class in the course
				for class_name in class_names:
					class_path=course_path+'/'+remove_non_path(class_name)

					# read data for the class
					with open(class_path+'/class.txt', 'r+') as class_file:
						class_data=[line.strip() for line in class_file.readlines()]

					# read available threads for the class
					with open(class_path+'/threads.txt', 'r+') as threads_file:
						thread_names=[line.strip() for line in threads_file.readlines()]

					# save the class
					clas=Class(class_data[0])
					course.classes[clas.name]=clas
					
					# for each thread in the class
					for thread_name in thread_names:

						# read data for the thread
						with open(class_path+'/'+thread_name+'/thread.txt') as thread_file:
							thread_data=[line.strip() for line in thread_file.readlines()]
						
						# save the thread
						thread=Thread(thread_data[0], thread_data[1], thread_data[2])
						clas.threads.add(thread)

	@staticmethod
	def add_to_cache(period, course=None, clas=None, thread=None):
		# appends path based on depth of new element
		# creates directory if it doesn't exist
		path='forum'
		pathlib.Path(os.getcwd()+'/'+path+'/'+period.path()).mkdir(parents=True, exist_ok=True)

		if course:
			path+='/'+period.path()
			pathlib.Path(os.getcwd()+'/'+path+'/'+course.path()).mkdir(parents=True, exist_ok=True)
		if clas:
			path+='/'+course.path()
			pathlib.Path(os.getcwd()+'/'+path+'/'+clas.path()).mkdir(parents=True, exist_ok=True)
		if thread:
			path+='/'+clas.path()
			pathlib.Path(os.getcwd()+'/'+path+'/'+thread.path()).mkdir(parents=True, exist_ok=True)

		# writes the appropriate file
		if thread:
			with open(path+'/threads.txt', 'a+') as list_file:
				list_file.write(thread.get_idx()+'\n')
			with open(path+'/'+thread.path()+'/thread.txt', 'w+') as thread_file:
				thread_file.write(thread.url+'\n'+thread.name+'\n'+thread.by+'\n')

		elif clas:
			with open(path+'/classes.txt', 'a+') as list_file:
				list_file.write(clas.name+'\n')
			with open(path+'/'+clas.path()+'/class.txt', 'w+') as class_file:
				class_file.write(clas.idx+'\n'+clas.name+'\n')
			with open(path+'/'+clas.path()+'/threads.txt', 'w+'): pass

		elif course:
			with open(path+'/courses.txt', 'a+') as list_file:
				list_file.write(course.name+'\n')
			with open(path+'/'+course.path()+'/course.txt', 'w+') as course_file:
				course_file.write(str(course.idx)+'\n'+course.name+'\n')		

		else:
			with open(path+'/periods.txt', 'a+') as list_file:
				list_file.write(period.name+'\n')
			with open(path+'/'+period.path()+'/period.txt', 'w+') as period_file:
				period_file.write(str(period.idx)+'\n'+period.name+'\n')		

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
		periods=Forum.find_periods(browser)

		# check for new periods
		for period in periods:
			# if period is new
			if period not in Forum.periods.values():
				Forum.add_to_cache(period)
				Forum.periods[period.idx]=period

		# get data for each period
		for period in Forum.periods.values():
			# select period in dropdown
			period_field.select_by_visible_text(period.name)

			# get available courses for the period
			print('Getting courses for', period.name)
			courses=Forum.find_courses(browser)

			# check for new courses in the period
			for course in courses:
				# if course is new
				if course not in period.courses.values():
					Forum.add_to_cache(period, course)
					period.courses[course.idx]=course
				
			# get data for each course in the period
			for course in period.courses.values():
				# select course in dropdown
				course_field.select_by_visible_text(course.name)
			
				# get available classes for each course
				print('Getting classes for', course.name)
				classes=Forum.find_classes(browser)
				
				# check for new classes in the period
				for clas in classes:
					if clas not in course.classes.values():
						Forum.add_to_cache(period, course, clas)
						course.classes[clas.idx]=clas

				# get data for each class
				for clas in course.classes.values():
					# select course in dropdown
					class_field.select_by_visible_text(clas.name)
					
					# get threads for the class
					print('Getting threads for', course.name, clas.name)
					threads=Forum.get_threads(browser)

					# check for new threads	
					for thread in threads:
						if thread not in clas.threads.values():
							# (TODO) delete this
							print('\nclas.threads:', clas.threads,'\n')
							# add new thread to notifications
							Notifications.add_forum_notification('New thread by '+thread.by+': '+thread.name)
							# add thread to database
							Forum.add_to_cache(period, course, clas, thread)
					clas.threads=threads

					# (TODO) delete later
					for thread in threads:
						print(thread.name, thread.by, thread.url, thread.get_idx(), '\n', sep='\n')

				print('===============================')
		

if __name__ == '__main__':
	try:
		Forum.load_cache()
	except FileNotFoundError as e:
		print(e)

	runPath = os.path.dirname(os.path.abspath(__file__))

	with initialise_browser(runPath) as (browser, _):
		Login.login(browser)
		Forum.get_forum_data(browser)
		if Notifications.has_notification:
			Notifications.notify()

	input()