# pylint: disable=unexpected-keyword-arg

from pathlib import Path
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import undetected_chromedriver as uc

PATH = Path(__file__).parent

options = webdriver.ChromeOptions()


class TikTokVideo:
    '''Takes video path and caption text to upload to Tiktok. Doesn't include auto-login.'''

    def __init__(
        self, driver=None,
        account='',
        caption='',
        video='',
    ):
        self.driver = driver or uc.Chrome(options=options)
        self.account = account
        self.caption = caption
        self.video = video

        self._cookies_file = PATH/'tmp'/'cookies.json'

        self.driver.maximize_window()
        self.driver.get('https://www.tiktok.com/about/contact?lang=en')
        self.load_cookies()

        # TODO: Add method for logging in via 2Captcha

    def save_cookies(self):
        '''Save all cookies in session'''
        with open(self._cookies_file, 'w+') as data:
            json.dump(self.driver.get_cookies(), data)

    def load_cookies(self):
        '''Load cookies from data dump into session'''
        if not self._cookies_file.is_file():
            with open(self._cookies_file, 'w+') as data:
                json.dump({}, data)

        with open(self._cookies_file, 'r') as data:
            for cookie in json.load(data):
                self.driver.add_cookie(cookie)

    def upload(self):
        '''Upload a specified video'''
        UPLOAD_HREF = 'https://www.tiktok.com/upload?lang=en'
        LOGIN_HREF = 'https://www.tiktok.com/login'

        self.driver.get(UPLOAD_HREF)

        if LOGIN_HREF in self.driver.current_url:
            print('Login needed to continue. Waiting for redirect to upload page.')
            WebDriverWait(self.driver, 3600).until(lambda _: UPLOAD_HREF in self.driver.current_url)

            print('Login successful!')
            self.save_cookies()
            self.driver.get(UPLOAD_HREF)  # Needed for selenium to wait for page to load.

        iframe = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//iframe')))
        self.driver.switch_to.frame(iframe)  # Wait and switch for Tiktok content iFrame

        upload = WebDriverWait(
            self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div/input[@type="file"]')))

        caption = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="notranslate public-DraftEditor-content"]')))

        post = WebDriverWait(
            self.driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//div[contains(@class, "btn-post")]/button')))

        caption.click()
        caption.send_keys(self.caption)

        upload.send_keys(self.video)

        WebDriverWait(
            self.driver, 3600).until(
            lambda _: post.is_enabled())  # Wait for post button to enable.

        post.click()

        time.sleep(0.5)  # TODO: Check if necessary.

        self.driver.quit()


# NOTE: Below is an example of use. Please note that class must be instantiated AND used inside __main__.
if __name__ == '__main__':
    cool = TikTokVideo(video=r'D:\Test\Directory\File.mp4', caption='Test')
    cool.upload()
