# For email sending
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Utilities
import getpass
import datetime
import time 
import configparser
import argparse
import os


def send_email(fromaddr,passwd,toaddr,subject,body):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, passwd)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print('Email has been sent successfully')

def scraper(driver, url):
    # - For elsevier:
    if 'elsevier' in url:    
        # Go to the URL
        driver.get(url)

        # Wait for page to load (could be improved)
        time.sleep(10)

        # Scrape relevant data
        #driver.save_screenshot('screenshot.png')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        status_str = ''
        status_str += soup.find(class_="lastupdate").text + '\n'
        status_str += soup.find(class_="statusstate").find('div').text + '\n'
        status_str += soup.find(class_="lastdate").find('div').text + '\n'
        for s in soup.find(class_="review-comments").find_all('li'):
            status_str += s.text + '\n'

        return status_str
    
    return None

if __name__=='__main__':
    #Argument parser
    parser=argparse.ArgumentParser(description='Scrape a track your paper link and send updates via email')
    parser._action_groups.pop()
    required=parser.add_argument_group('required arguments')
    optional=parser.add_argument_group('optional arguments')

    required.add_argument('-c','--config', type=str, help='Config file', required=True)

    optional.add_argument('--notify', default=False, action=argparse.BooleanOptionalAction)

    args=parser.parse_args()

    #Read config file
    config=configparser.ConfigParser()
    if os.path.isfile(args.config):
        config.read(args.config)
    else:
        raise FileNotFoundError('Could not load the configuration file.')

    print(config.sections())
    print(config['SMTP_AUTH']['USER'])
    print(config['Paper_1']['LINK'])
    print(config['Paper_1']['RECIPIENTS'].split(','))
    exit()

    url='https://track.authorhub.elsevier.com/?uuid=113968c5-1985-495c-855e-f75d8bbbc86e'

    # Set firefox to headless mode
    ffopt=webdriver.FirefoxOptions()
    ffopt.headless=True
    browser=webdriver.Firefox(options=ffopt)
    
    try:
        while True:
            for p in config.sections:
                if p == 'SMTP_AUTH':
                    continue
                # Scrape
                status = scraper(browser, config[p]['LINK'])

                # Read last status and send notice if anything changed
                if os.path.isfile(p + '.txt'):
                    # Read last status
                    with open(p + '.txt', 'r') as f:
                        last_status = f.read()
                    if status != last_status:
                        # Send email
                        send_email(
                            config['SMTP_AUTH']['USER'],
                            config['SMTP_AUTH']['PASSWD'],
                            config[p]['RECIPIENTS'].split(','),
                            f'{p}: paper tracker update', 
                            status
                            )
                        # Write new status
                        with open(p + '.txt', 'w') as f:
                            f.write(status)
                else:
                    # Write new status
                    with open(p + '.txt', 'w') as f:
                        f.write(status)

                    # Notify subscription
                    if args.notify:
                        # Send email
                        send_email(
                            config['SMTP_AUTH']['USER'],
                            config['SMTP_AUTH']['PASSWD'],
                            config[p]['RECIPIENTS'].split(','),
                            f'{p}: paper tracker subscription confirmation', 
                            status
                            )
            # Print log message
            print(f'Last check at: {str(datetime.datetime.now())}')
            
            # Wait for next loop (15 min)
            time.sleep(60) #60 sec for debugging
    except KeyboardInterrupt:
        #Quit the browser
        browser.close()
        browser.quit()

        print('Clean shutdown')

    