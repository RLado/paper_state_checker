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
import datetime
import time 
import configparser
import argparse
import os


def send_email(fromaddr,passwd,toaddr,subject,body):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    #msg['To'] = toaddr
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
    # Argument parser
    parser = argparse.ArgumentParser(description='Scrape a track your submission link and send updates via email')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-c','--config', type=str, help='Config file', required=True)

    optional.add_argument('--notify', default=False, action=argparse.BooleanOptionalAction)

    args=parser.parse_args()

    # Read config file
    config = configparser.ConfigParser()
    if os.path.isfile(args.config):
        config.read(args.config)
    else:
        raise FileNotFoundError('Could not load the configuration file.')
    
    # Main loop
    try:
        while True:
            #Read config file
            if os.path.isfile(args.config):
                config.read(args.config)
            else:
                raise FileNotFoundError('Could not load the configuration file.')
            
            # Set firefox to headless mode and start the browser
            ffopt=webdriver.FirefoxOptions()
            ffopt.headless=True
            browser=webdriver.Firefox(options=ffopt)

            # Scrape
            for p in config.sections():
                if p == 'SMTP_AUTH':
                    continue
                
                status = scraper(browser, config[p]['LINK'])
                if status == None:
                    print(f'ERROR: {p} did not yield any result!')
                    continue

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

            # Quit the browser
            browser.close()
            browser.quit()

            # Wait for next loop (10 min)
            for i in range(600):
                time.sleep(1)

    except KeyboardInterrupt:
        print('Done')
