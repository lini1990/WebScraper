import requests, os, threading, time
from fake_headers import Headers
from bs4 import BeautifulSoup

# Scraper proteinatlas
class Scraper(threading.Thread):
	def __init__(self, input_record):
		threading.Thread.__init__(self)
		self.input_record = input_record
		self.result = None
		
	def run(self):
		print("Scraper(): scrapRecord("+self.input_record["protein_description"]+"): Called")
		
		if self.input_record["protein_description"] == "": return
		
		r = requests.get("https://www.proteinatlas.org/search/{0}".format(self.input_record["protein_description"]), headers=Headers().generate())
		soup = BeautifulSoup(r.text, "html.parser")
		trs = soup.find("table", class_="searchResult").find("tbody").find_all("tr")
		for tr in trs:
			aTag = tr.find("a")
			if aTag.text == self.input_record["protein_description"]:
				r = requests.get("https://www.proteinatlas.org"+aTag["href"], headers=Headers().generate())
				soup = BeautifulSoup(r.text, "html.parser")
				
				tissue_specificity = soup.find_all("div", class_="summary_tag")[0].text
				tissue_expression_cluster = soup.find_all("div", class_="summary_tag")[1].text
				
				if tissue_specificity.lower().find("brain") >= 0 or tissue_expression_cluster.lower().find("brain") >= 0:
					specific = "yes"
				else:
					specific = "no"
								
				self.result = {"link":r.url, "tissue_specificity":tissue_specificity, "tissue_expression_cluster":tissue_expression_cluster, "specific": specific, "timestamp":int(time.time())}
				return

		return

