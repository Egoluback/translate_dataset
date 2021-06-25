from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

import pandas as pd
import numpy as np

import time

URL = "https://www.deepl.com/ru/translator"

class Parser:
	def __init__(self, language: str, data: pd.DataFrame, path: str, mode: str = "train"):
		self.language = language
		self.mode = mode
		self.data = data

		self.path = path

		self.load_point = 0
		self.errors_count = 0

		self.driver_start()

	def change_language(self):
		self.driver.find_element_by_class_name('lmt__language_select--target').click()
		postfix = "translator-lang-option-{0}-{1}".format(self.language, self.language.upper())

		if self.language == "en": postfix = "translator-lang-option-en-US"

		self.driver.find_element_by_xpath("//button[@dl-test = '{}']".format(postfix)).click()

	def driver_start(self):
		print("===DRIVER START===")
		self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

		self.driver.get(URL)

	def translate(self, text: str) -> str:
		self.change_language()
		self.driver.find_element_by_class_name("lmt__source_textarea").send_keys(text)
		response = self.driver.find_element_by_id("target-dummydiv").get_attribute('innerHTML')
		while len(response) == 2: response = self.driver.find_element_by_id("target-dummydiv").get_attribute('innerHTML')
		self.driver.get(URL)

		return response

	def Load(self):
		if len(self.data[(self.data.premise_trans == "0.0") | (self.data.hyp_trans == "0.0")].index) == 0: return
		self.load_point = self.data[(self.data.premise_trans == "0.0") | (self.data.hyp_trans == "0.0")].index[0]

	def is_clear(self, lineIndex: int) -> bool:
		return type(self.data["premise_trans"].iloc[lineIndex]) == str and len(self.data["premise_trans"].iloc[lineIndex]) > 3 and type(self.data["hyp_trans"].iloc[lineIndex]) == str and len(self.data["hyp_trans"].iloc[lineIndex]) > 3

	def Parse(self):
		print("Load point: {}".format(self.load_point))

		for lineIndex in range(self.load_point, len(self.data)):
			if self.is_clear(lineIndex): continue
			try:
				if lineIndex % 50 == 0:
					print("Backup...")
					print("Errors count: {}".format(self.errors_count))
					self.data.to_csv(self.path)

				print("Progress: {}%".format((lineIndex / len(self.data)) * 100))
				print("{0}/{1}".format(lineIndex, len(self.data)))

				self.data["premise_trans"].iloc[lineIndex] = self.translate(self.data.iloc[lineIndex].premise)
				self.data["hyp_trans"].iloc[lineIndex] = self.translate(self.data.iloc[lineIndex].hypothesis)

				time.sleep(0.5)

			except KeyboardInterrupt: break
			except: 
				print("===ERROR===")
				self.errors_count += 1
				self.driver_start()
				continue

def parse(parser: Parser) -> Parser:
	try:
		parser.Load()
		parser.Parse()
	except:
		print("===OUTER ERROR===")
		time.sleep(5)
		parser = parse(parser)

	return parser

language = input("Input dataset language: ")
mode = input("Input dataset mode: ")
path_setup = input("Input path to dataset: ")

print(f"---LANGUAGE: {language.upper()}")
print(f"---MODE: {mode.upper()}")

path = f"data/{mode}_{language}_translate.csv"

print(f"Translated file will be saved in {path}")

data = pd.read_csv(path_setup, engine='python', error_bad_lines=False)

if ("premise_trans" not in data.columns):
	data["premise_trans"] = np.zeros(data.shape[0])	
if ("hyp_trans" not in data.columns):
	data["hyp_trans"] = np.zeros(data.shape[0])

parser = parse(Parser(language, data, path, mode=mode))

print("Finish.")

parser.data.to_csv(path)

print("Saved.")