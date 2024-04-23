import pandas as pd
import requests as rq
from bs4 import BeautifulSoup as bs

url = "https://www.newschoolva.org/academics/course-catalog/"
reqHeaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"}

pg = rq.get(url, headers=reqHeaders)

pgHTML = pg.text
soup = bs(pgHTML, "html5lib")

headers = soup.find_all("strong")

print(str(headers))
