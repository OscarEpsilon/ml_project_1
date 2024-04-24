import pandas as pd
import requests as rq
import bs4

catalogURL = "https://www.newschoolva.org/academics/course-catalog/"
reqHeaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"}

catalogRes = rq.get(catalogURL, headers=reqHeaders)
catalogHTML = catalogRes.text
catalogSoup = bs4.BeautifulSoup(catalogHTML, "html5lib")

COURSES_TITLE_KEY = "title"
COURSES_CREDIT_KEY = "credit"
COURSES_DESC_KEY = "description"

def getCourseInfo(titleTag: bs4.Tag) -> dict:
    # Some courses have their line break nested inside their strong tag instead of outside
    brInsideStrong = False
    if len(titleTag.contents) == 2:
        courseTitle = next(titleTag.children).string
        brInsideStrong = True
    else:
        courseTitle = titleTag.string
    
    # There are a few weird individual exceptions
    # This is the only one with the unique exception of having a
    # random empty strong tag placed in the middle of it--so
    # we just don't even bother to make exceptions for all of them here
    if courseTitle == "Collage Studio":
        return {COURSES_TITLE_KEY: courseTitle,
                COURSES_CREDIT_KEY: "Arts 1",
                COURSES_DESC_KEY: "Students will work with mixed media techniques to create various collage artworks. Students can expect to work in 2D, 3D, and digital art mediums to develop their collages. EQ: How can pre-existing images and materials be repurposed to create a new meaning?"}
    
    # Also this one
    if courseTitle == "Poetry, English 1":
        return {COURSES_TITLE_KEY: "Poetry",
                COURSES_CREDIT_KEY: "English 1",
                COURSES_DESC_KEY: "Poetry is an art that can be written, spoken, or performed–it is a total experience of language. To appreciate this art, we must learn the tools and techniques employed by the artists in its creation, and then study the end effect. You’ll be expected, early on, merely to respond to the poems in a human way. As we begin to share some ideas of what a poem is, what it does, and how, and why–we’ll explore the poems on a more sophisticated level. We will read a lot of poems, both traditional and those that break from tradition, and we will also craft and share our own poetry in an attempt to answer the question: How does the poet use all the tools at their disposal to create an experience in the reader?"}
    
    # And this one
    if courseTitle == "Mid-Century Crossroads":
        return {COURSES_TITLE_KEY: "Mid-Century Crossroads: The 1950s and 60s",
                COURSES_CREDIT_KEY: "US History 1",
                COURSES_DESC_KEY: "The mid twentieth century witnessed intensely accelerated change in American society. Following World War II, political, economic, and social patterns led to widespread divisions within America. A time which appeared prosperous and idyllic on the surface came to an abrupt halt as Black Americans and women demanded civil rights, America’s youth became disillusioned, and conflicts arose between the generations. This course analyzes the causes and effects of this time period and its permanent impact on American culture."}

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
    
    # If a course credit is given, it must be the next sibling with index 0, and it must have the str type
    # Otherwise, we know it is a math credit
    if type(courseInfo[0]) == bs4.NavigableString and not brInsideStrong:
        courseCredit = courseInfo[0][(2 - numTitleExtraEndBoldLetters):]
        
        # Some course credits end with a space
        if courseCredit[-1:] == " ":
            courseCredit = courseCredit[:-1]
        
        # Some end with " (", sometimes the case if it is open to 8th graders
        if courseCredit[-2:] == " (":
            courseCredit = courseCredit[:-2]
    
    else:
        courseCredit = "Math"
    
    courseDescTags = []

    if brInsideStrong:
        courseDescTags = list(titleTag.next_siblings)
    else:
        courseDescTags = list(titleTag.findNextSibling(name="br").next_siblings)
    
    for thisCourseDescTag in courseDescTags:
        if thisCourseDescTag.name != "br":
            courseDesc += thisCourseDescTag.string
    
    return {COURSES_TITLE_KEY: courseTitle, COURSES_CREDIT_KEY: courseCredit, COURSES_DESC_KEY: courseDesc}

titleTags = catalogSoup.find_all("strong")

# One strong tag is an empty whitespace in the middle of the course catalog and should not be there
for tagIndex, thisTag in enumerate(titleTags):
    if thisTag.string == " ":
        del(titleTags[tagIndex])

courseDicts = list(map(getCourseInfo, titleTags))
courseDF = pd.DataFrame(courseDicts)
courseDF.to_csv("courses.csv")
