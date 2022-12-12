
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import datetime
import time 


url='https://track.authorhub.elsevier.com/?uuid=113968c5-1985-495c-855e-f75d8bbbc86e'

#Set firefox to headless mode
ffopt=webdriver.FirefoxOptions()
ffopt.headless=True

#Create web driver object and go to the URL
browser=webdriver.Firefox(options=ffopt)
browser.get(url)

#Wait for page to load
time.sleep(10)

#Scrape relevant data
#browser.save_screenshot('screenie.png')
soup = BeautifulSoup(browser.page_source, 'html.parser')

status_str = ''
status_str += soup.find(class_="lastupdate").text + '\n'
status_str += soup.find(class_="statusstate").find('div').text + '\n'
status_str += soup.find(class_="lastdate").find('div').text + '\n'
for s in soup.find(class_="review-comments").find_all('li'):
    status_str += s.text + '\n'

print(status_str)

#Quit the browser
browser.close()
browser.quit()

#Print log message
print(f'Last check at: {str(datetime.datetime.now())}')