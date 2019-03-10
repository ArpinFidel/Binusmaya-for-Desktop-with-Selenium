from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from time import sleep

import pathlib
import pickle
import os

from lib.notifications import Notifications

import lib.browseractions as browseractions
import lib.login as login

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

class Category:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return self.name==other.name
	
	def __ne__(self, other):
		return self.name!=other.name

	def __hash__(self):
		return hash(self.name)

	def __repr__(self):
		return self.name

	def path(self):
		return browseractions.remove_non_path(self.name)

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
		
class Thread(Category):
	def __init__(self, url, name, by):
		super().__init__(name)
		self.url = url
		self.by = by
		if url[-5:] != '?id=1': raise ValueError('Unexpected url suffix')

	def get_idx(self):
		return self.url.split('.')[-1][:-5]
	
	def path(self):
		return browseractions.remove_non_path(self.get_idx())

periods={}

def __init__(self):
    pass


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


def save_data():
    pathlib.Path(os.getcwd()+'/forum').mkdir(parents=True, exist_ok=True)
    with open('forum/forum.pkl', 'wb+') as f:
        pickle.dump(periods, f, pickle.HIGHEST_PROTOCOL)


def load_data():
    global periods
    with open('forum/forum.pkl', 'rb') as f:
        periods=pickle.load(f)


def fetch_data(browser):
    
    # load the page
    print('Loading forum')
    login.load_url(browser, forum_url)
    
    # wait for page to render
    print('Wating for page to render')
    sleep(3)
    
    # get fields
    print('Getting forum fields')
    period_field, course_field, class_field=find_forum_fields(browser)
    
    # get available periods
    print('Getting all available periods')
    periods=find_periods(browser)

    # check for new periods
    for period in periods:
        # if period is new
        if period not in periods:
            periods[period.name]=period

    # get data for each period
    for period in periods:
        # select period in dropdown
        period_field.select_by_visible_text(period.name)

        # get available courses for the period
        print('Getting courses for', period.name)
        courses=find_courses(browser)

        # check for new courses in the period
        for course in courses:
            # if course is new
            if course not in period.courses.values():
                period.courses[course.name]=course
            
        # get data for each course in the period
        for course in period.courses.values():
            # select course in dropdown
            course_field.select_by_visible_text(course.name)
        
            # get available classes for each course
            print('Getting classes for', course.name)
            classes=find_classes(browser)
            
            # check for new classes in the period
            for clas in classes:
                if clas not in course.classes.values():
                    course.classes[clas.name]=clas

            # get data for each class
            for clas in course.classes.values():
                # select course in dropdown
                class_field.select_by_visible_text(clas.name)
                
                # get threads for the class
                print('Getting threads for', course.name, clas.name)
                threads=get_threads(browser)

                # check for new threads	
                for thread in threads:
                    if thread not in clas.threads:
                        # add new thread to notifications
                        Notifications.add_forum_notification('New thread by '+thread.by+': '+thread.name)
                clas.threads=threads
                
    save_data()
