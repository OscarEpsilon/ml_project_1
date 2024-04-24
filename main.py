import pandas as pd
import requests as rq
import bs4

url = "https://www.newschoolva.org/academics/course-catalog/"
reqHeaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"}

pg = rq.get(url, headers=reqHeaders)

pgHTML = pg.text
soup = bs4.BeautifulSoup(pgHTML, "html5lib")

def getCourseInfo(titleTag: bs4.Tag) -> dict:
    # Some courses have their line break nested inside their strong tag instead of outside
    if len(titleTag.contents) == 2:
        courseTitle = next(titleTag.children)
    else:
        courseTitle = titleTag.string

    # Some courses have an unbolded letter at the start of their title
    prevSibling = titleTag.previous_sibling
    if prevSibling != None:
        courseTitle = prevSibling.string + courseTitle
    
    # Some courses have a bolded comma at the end of the title
    if courseTitle[-1:] == ",":
        courseTitle = courseTitle[:-1]
    
    courseInfo = list(titleTag.next_siblings)

    courseCredit = ""
    courseDesc = ""

    descSearchStartIndex = 1
    
    # If a course credit is given, it must be the next sibling with index 0, and it must have the str type
    # Otherwise, we know it is a math credit
    if type(courseInfo[0]) == bs4.NavigableString:
        courseCredit = courseInfo[0][2:]
    else:
        courseCredit = "Math"
        descSearchStartIndex = 0
    
    for thisInfo in courseInfo[descSearchStartIndex:]:
        if type(thisInfo) == bs4.NavigableString:
            courseDesc = thisInfo
            break
    
    return {"title": courseTitle, "credit": courseCredit, "desc": courseDesc}

titleTags = soup.find_all("strong")
courseDicts = list(map(getCourseInfo, titleTags))
courseDF = pd.DataFrame(courseDicts)
courseDF.to_csv("courses.csv")