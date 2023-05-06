import concurrent.futures
import math
import re
import requests
import config
from lxml import html
import json
from tools import Tools
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import saver
import scraper


class Crawler:
    def __init__(self):
        self.__proxy_socket = None
        self.__tools_obj = Tools()
        self.__logger = Tools().get_logger("./")
        self.__scraper = scraper.Scraper()
        self.__saver = saver.Saver()
        self.__totalJobsUrls = []
        self.__totalJobsData = []
        self.__startURL = config.startURL.format(config.where, config.page, config.keywords)

    def crawl_request(self):
        try:
            self.logging('Starting crawler at {}'.format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")))
            # Search merchants iterating id and save into excel file
            self.pagination(self.__startURL)
            self.scraping(self.__totalJobsUrls)

            self.logging('Crawler ends at {}'.format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")))
        except Exception as e:
            self.logging('ERROR at crawl_request - {}'.format(e))

    def pagination(self, startURL):
        try:
            # Calculate num of pages
            response_raw = self.try_request(startURL)
            response_json = json.loads(response_raw.text)
            totalItems = response_json["totalCount"]
            calc_pages = totalItems / 22
            pages = math.ceil(calc_pages)

            with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as executor:
                for page in range(1, pages + 1):
                    # Create job url
                    executor.submit(self.parallel_pagination, page)
        except Exception as e:
            self.logging('ERROR at - {}'.format(e))

    def scraping(self, jobs_list):
        self.logging('Scraping process starting at {}'.format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")))
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as executor:
                for url in jobs_list:
                    self.logging('Scraping job')

                    executor.submit(self.parallel_scraping, url)

            self.__saver.saver(self.__totalJobsData)
        except Exception as e:
            self.logging('ERROR in scraping - {}'.format(e))

    def try_request(self, url, proxy=None):
        try:
            if proxy:
                http_proxy = f"http://{proxy}"
                proxies = {
                    "http": http_proxy,
                    "https": http_proxy,
                }
                response = requests.request("GET", url, proxies=proxies)
            else:
                response = requests.request("GET", url)
            return response
        except Exception as e:
            self.logging('ERROR in executor - {}'.format(e))

    def logging(self, text):
        self.__logger.info(text)

    def parallel_pagination(self, page):
        try:
            self.logging('Page {}'.format(page))
            response_raw = self.try_request(config.startURL.format(config.where, page, config.keywords))
            response_json = json.loads(response_raw.text)
            jobs_list = response_json['data']
            for job in jobs_list:
                job_id = job['id']
                # Build Job url
                job_url = config.jobURL + str(job_id)
                self.__totalJobsUrls.append(job_url)
        except Exception as e:
            self.logging('ERROR at parallel_pagination - {}'.format(e))
        pass

    def parallel_scraping(self, url):
        try:
            # Extraemos JSON del html
            response_raw = self.try_request(url)
            response_html = html.fromstring(response_raw.text)

            responseJson_raw = response_html.xpath('//script[@data-automation]/text()')[0]
            responseJson_raw = re.findall('.*window\.SEEK_REDUX_DATA = (.*)?;', responseJson_raw)[0]
            responseJson_raw = re.sub(r'undefined', 'null', responseJson_raw)

            responseJson = json.loads(responseJson_raw)
            jobJson = responseJson["jobdetails"]["result"]["job"]

            result_dict = self.__scraper.create_dict(jobJson)
            self.__totalJobsData.append(result_dict)
        except Exception as e:
            self.logging('ERROR in parallel_scraping - {}'.format(e))
