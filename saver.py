import openpyxl
import os
from tools import Tools


class Saver:
    def __init__(self):
        self.__tools_obj = Tools()
        self.__logger = Tools().get_logger("./")

    def logging(self, text):
        self.__logger.info(text)

    def saver(self, result_dict):
        try:
            for result in result_dict:
                headers = list(result.keys())
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
                row = [value for value in result.values()]
                self.logging('Saving in excel')
                worksheet.append(row)
                # Save the workbook to the file
                workbook.save('results.xlsx')
        except Exception as e:
            self.logging('ERROR in saver() - {}'.format(e))
