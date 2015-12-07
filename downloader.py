from time import sleep
import urllib3
import shutil
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class ConvertToMp3Downloader:
    def __init__(self, youtube_video_id: str):
        self.youtube_url = "https://www.youtube.com/watch?v=" + youtube_video_id
        self.driver = webdriver.PhantomJS()

    def set_album_title(self, title: str):
        self.album_title = title

    def download_as_mp3(self, download_folder: str):
        if not download_folder.endswith("/"):
            download_folder += "/"

        ####
        ### CONVERT SONG
        ####
        self.driver.get("http://www.convert2mp3.net")
        elem = self.driver.find_element_by_id("urlinput")
        elem.send_keys(self.youtube_url)
        elem.send_keys(Keys.RETURN)

        if "Das Video ist länger als 90 Minuten" in self.driver.page_source:
            raise DownloadException("Unable to download video '{0}' which is longer than 90 minutes".format(self.youtube_url))

        if "Es ist ein Fehler aufgetreten" in self.driver.page_source:
            raise DownloadException("Error while downloading '{0}' via convert2mp3.net".format(self.youtube_url))

        # Wait for conversion
        WebDriverWait(self.driver, 200).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "btn-success"))
        )

        ####
        ### SET AND GET ATTRIBUTES
        ####

        # Open advanced settings
        self.driver.find_element_by_id("advancedtags_btn").click()
        sleep(1)  # Wait for animation

        # Get artist (first option!)
        first_artist_option = self.driver.find_element_by_xpath("//*[@id='inputArtist']/option[1]")
        self.artist = first_artist_option.get_attribute("value")

        # Get song title
        def find_correct_title(title_options) -> str:
            for title_option in title_options:
                title = title_option.get_attribute("value")
                if title != self.artist and "(" not in title and ")" not in title and "/" not in title:
                    return title
            raise Exception("No suitable title found!")

        title_options = self.driver.find_elements_by_xpath("//*[@id='inputTitle']//option")
        self.title = find_correct_title(title_options)

        # Album
        if hasattr(self, "album_title"):
            self.driver.find_element_by_id("inputAlbum").send_keys(self.album_title)

        # Set Cover as mp3 picture
        elem = self.driver.find_element_by_id("inputCover")
        elem.click()

        elem = self.driver.find_element_by_class_name("btn-success")
        elem.click()

        ####
        ### DOWNLOAD
        ####
        download_url = self.driver.find_element_by_class_name("btn-success").get_attribute("href")
        file_name = "{0}-{1}.mp3".format(self.artist, self.title)
        full_download_path = (download_folder + file_name).encode("utf-8")

        download(download_url, full_download_path)

        self.driver.close()

    def download_as_mp4(self, download_folder: str):
        if not download_folder.endswith("/"):
            download_folder += "/"

        ####
        ### CONVERT VIDEO
        ####
        self.driver.get("http://www.convert2mp3.net")
        elem = self.driver.find_element_by_id("urlinput")
        elem.send_keys(self.youtube_url)

        # Select MP4 as container
        self.driver.find_element_by_class_name("dropdown-toggle").click()
        self.driver.find_element_by_xpath("//*[@id='convertForm']/fieldset/div[1]/div/ul/li[7]/a").click()

        elem.send_keys(Keys.RETURN)
        assert "Es ist ein Fehler aufgetreten" not in self.driver.page_source

        # Wait for conversion
        WebDriverWait(self.driver, 200).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "btn-success"))
        )

        ####
        ### DOWNLOAD
        ####
        download_url = self.driver.find_element_by_class_name("btn-success").get_attribute("href")
        file_name = self.driver.find_element_by_xpath("/html/body/div[3]/div/div[1]/div[2]/div[2]/div/a").get_attribute("data-filename")
        full_download_path = (download_folder + file_name).encode("utf-8")

        download(download_url, full_download_path)

        self.driver.close()

def download(url:str, path:str):
    http = urllib3.PoolManager()
    with http.request('GET', url, preload_content=False) as resp, open(path, 'wb') as out_file:
        shutil.copyfileobj(resp, out_file)

class DownloadException(Exception):
    pass