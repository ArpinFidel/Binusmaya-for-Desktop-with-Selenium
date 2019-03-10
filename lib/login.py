from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from getpass import getpass

import lib.browseractions as browseractions

login_url='https://binusmaya.binus.ac.id/login/'
	
username_field_xpath='//*[@id="login"]/form/div[1]/label/input'
password_field_xpath='//*[@id="login"]/form/p[1]/span/input'
login_button_css='.button.button-primary.wide'

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
    

def is_logged_in(browser):
    user_name_xpath='//*[@id="aUsername"]'
    try:
        browser.find_element(By.XPATH, user_name_xpath)
    except:
        return False
    else:
        return True


def find_login_elements(browser):
    exceptions=[]
    for _ in range(5):
        try:
            elements=(
                browser.find_element(By.XPATH, username_field_xpath)
                , browser.find_element(By.XPATH, password_field_xpath)
                , browser.find_element(By.CSS_SELECTOR, login_button_css)
                )
            break
        except Exception as e:
            exceptions.append(e)
            sleep(0.5)	
    else: raise Exception(TimeoutError('Cannot find login fields'), exceptions)
    
    return elements


def login(browser):
    
    print('Logging in')
    login_exceptions=[]
    for _ in range(10):
        try:
            print('Getting credentials')
            username, password = get_credentials()
            
            browser.get(login_url)
            
            print('Trying to find login fields')
            username_field, password_field, login_button=find_login_elements(browser)
            
            print('Entering credentials')
            username_field.send_keys(username)
            password_field.send_keys(password)
            login_button.click()
            
            sleep(0.25)
            if is_logged_in(browser): break
        except Exception as e:
            login_exceptions.append(e)
            sleep(0.5)
        else:
            sleep(0.5)
            if not is_logged_in(browser): login_exceptions.add(Exception('Server is not responding'))
    else: raise Exception(TimeoutError('Cannot login'), login_exceptions)
    
    print('Stopping browser from redirecting')
    browseractions.stop_loading(browser)
    
    print('Finished login')


def handle_session_timeout(browser):
    try:
        browser.switch_to.alert.accept()
    except:
        if is_logged_in(browser): return
        
    browseractions.stop_loading(browser)
    login(browser)

def load_url(browser, url):
	for _ in range(20):
		if browser.current_url == url: break
		browser.get(url)
		if is_logged_in(browser): break
		handle_session_timeout(browser)
		sleep(0.5)
