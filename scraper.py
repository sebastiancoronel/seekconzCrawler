from lxml import html
from datetime import datetime
import time
import json
import re
from tools import Tools


class Scraper:

    def __init__(self):
        self.__proxy_socket = None
        self.__tools_obj = Tools()
        self.__logger = Tools().get_logger("./")

    def logging(self, text):
        self.__logger.info(text)

    def create_dict(self, jobJson):
        if jobJson["id"] == '67113436':
            print("XX")
            pass
        self.logging('Scraping - {}'.format(jobJson["shareLink"]))
        result_dict = {"titulo": None,
                       "telefono_1": None,
                       "telefono_2": None,
                       "telefono_3": None,
                       "telefono_4": None,
                       "telefono_5": None,
                       "resumen": None,
                       "contenido": None,
                       "tipo": None,  # part time o full time
                       "salario": None,
                       "ubicacion": None,
                       "email_1": None,
                       "email_2": None,
                       "email_3": None,
                       "email_4": None,
                       "email_5": None,
                       "link": None,
                       }

        # Extract the data from the JSON
        try:
            # Remove tags from content:
            content = re.sub('<[^<]+?>', "", jobJson["content"])
            result_dict["titulo"] = jobJson["title"]
            result_dict["telefono_1"] = jobJson["phoneNumber"]
            # Telefonos extras
            phone_list = re.findall('\d(?:\s?\d){5,}', content)
            if len(phone_list) > 0:
                try:
                    result_dict["telefono_2"] = re.findall('\d(?:\s?\d){5,}', content)[0]
                    result_dict["telefono_3"] = re.findall('\d(?:\s?\d){5,}', content)[1]
                    result_dict["telefono_4"] = re.findall('\d(?:\s?\d){5,}', content)[2]
                    result_dict["telefono_5"] = re.findall('\d(?:\s?\d){5,}', content)[3]
                except Exception as e:
                    pass

            # Emails
            email_list = re.findall(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', content)
            if len(email_list) > 0:
                try:
                    result_dict["email_1"] = \
                        re.findall(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', content)[0]
                    result_dict["email_2"] = \
                        re.findall(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', content)[1]
                    result_dict["email_3"] = \
                        re.findall(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', content)[2]
                    result_dict["email_4"] = \
                        re.findall(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', content)[3]
                except Exception as e:
                    pass

            try:
                result_dict["salario"] = jobJson["salary"]["label"]
            except Exception as e:
                pass
            result_dict["resumen"] = jobJson["abstract"]
            result_dict["tipo"] = jobJson["workTypes"]["label"]
            result_dict["ubicacion"] = jobJson["location"]["label"]
            result_dict["contenido"] = content
            result_dict["link"] = jobJson["shareLink"]

        except Exception as e:
            self.logging('ERROR in scraper() - {}'.format(e))

        # Save the extracted data
        if result_dict:
            return result_dict
