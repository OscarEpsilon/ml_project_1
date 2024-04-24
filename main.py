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
    brInsideStrong = False
    if len(titleTag.contents) == 2:
        courseTitle = next(titleTag.children).string
        brInsideStrong = True
    else:
        courseTitle = titleTag.string
    
    # This is the only one with the unique exception of having a
    # random empty strong tag placed in the middle of it--so
    # we just don't even bother to make exceptions for all of them here
    if courseTitle == "Collage Studio":
        return {"title": courseTitle,
                "credit": "Arts 1",
                "desc": "Students will work with mixed media techniques to create various collage artworks. \
                    Students can expect to work in 2D, 3D, and digital art mediums to develop their collages. \
                    EQ: How can pre-existing images and materials be repurposed to create a new meaning?"}

    # Some courses have an unbolded letter at the start of their title
    prevSibling = titleTag.previous_sibling
    if prevSibling != None:
        courseTitle = prevSibling.string + courseTitle
    
    numTitleExtraEndBoldLetters = 0
    
    # Some courses have a bolded comma at the end of the title
    # Some also have an extra space as well
    if courseTitle[-1:] == ",":
        courseTitle = courseTitle[:-1]
        numTitleExtraEndBoldLetters = 1
    elif courseTitle[-2:] == ", ":
        courseTitle = courseTitle[:-2]
        numTitleExtraEndBoldLetters = 2
    
    courseInfo = list(titleTag.next_siblings)

    courseCredit = ""
    courseDesc = ""

    descSearchStartIndex = 1
    
    # If a course credit is given, it must be the next sibling with index 0, and it must have the str type
    # Otherwise, we know it is a math credit
    if type(courseInfo[0]) == bs4.NavigableString and not brInsideStrong:
        courseCredit = courseInfo[0][(2 - numTitleExtraEndBoldLetters):]
        
        # Some course credits end with a space
        if courseCredit[-1:] == " ":
            courseCredit = courseCredit[:-1]
        
        # Some end with " ("
        if courseCredit[-2:] == " (":
            courseCredit = courseCredit[:-2]
    
    else:
        courseCredit = "Math"
        descSearchStartIndex = 0
    
    courseDescTags = []

    if brInsideStrong:
        courseDescTags = list(titleTag.next_siblings)
    else:
        courseDescTags = list(titleTag.findNextSibling(name="br").next_siblings)
    
    for thisCourseDescTag in courseDescTags:
        if thisCourseDescTag.name != "br":
            courseDesc += thisCourseDescTag.string
    
    return {"title": courseTitle, "credit": courseCredit, "desc": courseDesc}

titleTags = soup.find_all("strong")

# One strong tag is an empty whitespace in the middle of the course catalog and should not be there
for tagIndex, thisTag in enumerate(titleTags):
    if thisTag.string == " ":
        del(titleTags[tagIndex])

courseDicts = list(map(getCourseInfo, titleTags))
courseDF = pd.DataFrame(courseDicts)
courseDF.to_csv("courses.csv")