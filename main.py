import pandas
import requests as rq

url = "https://www.newschoolva.org/academics/course-catalog/"

page = rq.get(url)

print(page.text)
