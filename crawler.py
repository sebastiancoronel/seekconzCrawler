import concurrent.futures
import math
import os
import re
import lxml.html
import requests
import config
from lxml import html
import json
import csv
from tools import Tools
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import openpyxl


class Crawler:
    def __init__(self):
        self.__proxy_socket = None
        self.__tools_obj = Tools()
        self.__logger = Tools().get_logger("./")
        self.__totalJobsUrls = []
        self.__startURL = config.startURL.format(config.where, config.page, config.keywords)

    def crawl_request(self):
        try:
            self.logging('Starting crawler at {}'.format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")))
            # Search merchants iterating id and save into excel file
            self.pagination(self.__startURL)
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
                for page in range(1, pages+1):
                    # Create job url
                    executor.submit(self.parallel_pagination, page)
        except Exception as e:
            self.logging('ERROR at - {}'.format(e))

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

    def scraper(self, seller):
        self.logging('Scraping process starting at {}'.format(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")))

        # Make a request to the seller's page and extract the JSON data
        response = self.try_request(seller)
        htmlresponse = html.fromstring(response.content)

        # Extract JSON from html tree
        responseJson_raw = htmlresponse.xpath('//script[@id="__NEXT_DATA__"]/text()')
        responseJson = json.loads(responseJson_raw[0])

        # Initialize a dictionary to store the extracted data
        result_dict = {"url": None,
                       "name": None,
                       "impressum": None,
                       "productsAmount": None,
                       }
        # Extract the data from the JSON
        try:
            result_dict["name"] = responseJson['props']["pageProps"]["name"]
            result_dict["impressum"] = re.sub(r'^(Impressum|Imprint):', '',
                                              responseJson['props']["pageProps"]["description"],
                                              flags=re.IGNORECASE | re.MULTILINE)
            result_dict["productsAmount"] = responseJson['props']["pageProps"]["productCount"]
            result_dict["url"] = seller
        except Exception as e:
            self.logging('ERROR in scraper() - {}'.format(e))

        # Save the extracted data
        if result_dict:
            self.saver(result_dict)

    def saver(self, result_dict):
        try:
            headers = list(result_dict.keys())
            # If the file doesn't exist, create a new workbook and add a new worksheet
            if not os.path.exists('results.xlsx'):
                workbook = openpyxl.Workbook()
                worksheet = workbook.active
                worksheet.append(headers)

            # If the file exists, open it and add the results to the existing worksheet
            else:
                workbook = openpyxl.load_workbook('results.xlsx')
                worksheet = workbook.active
            # Get the values from the result dictionary and add them as a new row in the worksheet
            row = [value for value in result_dict.values()]
            self.logging('Saving in excel {}'.format(result_dict["name"]))
            worksheet.append(row)
            # Save the workbook to the file
            workbook.save('results.xlsx')
        except Exception as e:
            self.logging('ERROR in saver() - {}'.format(e))

    def logging(self, text):
        self.__logger.info(text)

    def parallel_pagination(self, page):
        response_raw = self.try_request(config.startURL.format(config.where, page, config.keywords))
        response_json = json.loads(response_raw.text)
        jobs_list = response_json['data']
        for job in jobs_list:
            job_id = job['id']
            # Build Job url
            job_url = config.jobURL + str(job_id)
            self.__totalJobsUrls.append(job_url)
        return True

        # if response.status_code == 500:
        #     self.logging('Seller Not Found {}'.format(url))
        # elif response.status_code == 200:
        #     self.logging('New seller found at - {}'.format(url))
        #     self.scraper(url)
