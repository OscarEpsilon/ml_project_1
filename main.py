from typing import Final

import pandas as pd
import requests as rq
import bs4

CATALOG_URL: Final[str] = "https://www.newschoolva.org/academics/course-catalog/"
CATALOG_REQ_HEADERS: Final[dict[str, str]] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"}

COURSES_TITLE_KEY: Final[str] = "title"
COURSES_CREDITS_KEY: Final[str] = "credits"
COURSES_LEVEL_KEY: Final[str] = "level"
COURSES_DESC_KEY: Final[str] = "description"

catalogRes: Final[rq.Response] = rq.get(CATALOG_URL, headers=CATALOG_REQ_HEADERS)
catalogHTML: Final[str] = catalogRes.text
catalogSoup: Final[bs4.BeautifulSoup] = bs4.BeautifulSoup(catalogHTML, "html5lib")

courseDicts: list[dict[str, str | None | list[str]]] = list[dict[str, str | None | list[str]]]()

def parseCourseLevel(strWithLevel: str) -> str | None:
    if strWithLevel.find(" 1/2") != -1:
        return "1/2"
    elif strWithLevel.find(" 1") != -1:
        return "1"
    elif strWithLevel.find(" 2") != -1:
        return "2"
    elif strWithLevel.find(" 3") != -1:
        return "3"
    elif strWithLevel.find("Advanced ") != -1:
        return "Advanced"
    elif strWithLevel.find("Honors ") != -1:
        return "Honors"
    return None

# Cleanup credit string and remove course level
def cleanCreditStr(courseCreditStr: str) -> str:
    return courseCreditStr.replace(" Level ", " ").replace(" 1/2", "").replace(" 1", "").replace(" 2", "").replace("Honors ", "").replace("PE/Health", "PE+Health").replace("/", ", ").replace("PE+Health", "PE/Health").replace(", or ", ", ").replace(" or ", ", ").replace("Arts", "Art")

def parseCourseCreditStr(courseCreditStr: str) -> tuple[list[str], str | None]:
    courseCredits: list[str] = cleanCreditStr(courseCreditStr).split(", ")
    courseLevel: str | None = parseCourseLevel(courseCreditStr)

    return (courseCredits, courseLevel)

def getCourseInfo(titleTag: bs4.Tag) -> dict[str, str | None | list[str]] | None:
    courseTitle: str = ""

    # Some courses have their line break nested inside their strong tag instead of outside, breaking titleTag.string
    courseTitleAtt: str | None = titleTag.string
    brInsideStrong: bool = False
    if courseTitleAtt == None:
        courseTitle = next(titleTag.children).string # type: ignore
        brInsideStrong = True
    else:
        courseTitle = courseTitleAtt

    # There are a few weird individual exceptions
    # This is the only one with the unique exception of having a
    # random empty strong tag placed in the middle of it--so
    # we just don't even bother to make exceptions for all of them here
    if courseTitle == "Collage Studio":
        return {COURSES_TITLE_KEY: courseTitle,
                COURSES_CREDITS_KEY: ["Art"],
                COURSES_LEVEL_KEY: "1",
                COURSES_DESC_KEY: "Students will work with mixed media techniques to create various collage artworks. Students can expect to work in 2D, 3D, and digital art mediums to develop their collages. EQ: How can pre-existing images and materials be repurposed to create a new meaning?"}

    # Also this one
    if courseTitle == "Poetry, English 1":
        return {COURSES_TITLE_KEY: "Poetry",
                COURSES_CREDITS_KEY: ["English"],
                COURSES_LEVEL_KEY: "1",
                COURSES_DESC_KEY: "Poetry is an art that can be written, spoken, or performed–it is a total experience of language. To appreciate this art, we must learn the tools and techniques employed by the artists in its creation, and then study the end effect. You’ll be expected, early on, merely to respond to the poems in a human way. As we begin to share some ideas of what a poem is, what it does, and how, and why–we’ll explore the poems on a more sophisticated level. We will read a lot of poems, both traditional and those that break from tradition, and we will also craft and share our own poetry in an attempt to answer the question: How does the poet use all the tools at their disposal to create an experience in the reader?"}

    # And this one
    if courseTitle == "Mid-Century Crossroads":
        return {COURSES_TITLE_KEY: "Mid-Century Crossroads: The 1950s and 60s",
                COURSES_CREDITS_KEY: ["US History"],
                COURSES_LEVEL_KEY: "1",
                COURSES_DESC_KEY: "The mid twentieth century witnessed intensely accelerated change in American society. Following World War II, political, economic, and social patterns led to widespread divisions within America. A time which appeared prosperous and idyllic on the surface came to an abrupt halt as Black Americans and women demanded civil rights, America’s youth became disillusioned, and conflicts arose between the generations. This course analyzes the causes and effects of this time period and its permanent impact on American culture."}

    # Some courses have an unbolded letter at the start of their title
    prevSibling: bs4.PageElement | None = titleTag.previous_sibling
    if type(prevSibling) == bs4.NavigableString:
        courseTitle = prevSibling + courseTitle

    numTitleExtraEndBoldLetters: int = 0

    # Some courses have a bolded comma at the end of the title
    # Some also have an extra space as well
    if courseTitle[-1:] == ",":
        courseTitle = courseTitle[:-1]
        numTitleExtraEndBoldLetters = 1
    elif courseTitle[-2:] == ", ":
        courseTitle = courseTitle[:-2]
        numTitleExtraEndBoldLetters = 2

    courseInfoTags: Final[list[bs4.PageElement]] = list(titleTag.next_siblings)

    courseCreditStr: str = ""
    courseDesc: str = ""

    # If a course credit is given, it must be the next sibling with index 0, and it must have the str type
    # Otherwise, we know it is a math credit
    if type(courseInfoTags[0]) == bs4.NavigableString and not brInsideStrong:
        courseCreditStr = courseInfoTags[0][(2 - numTitleExtraEndBoldLetters):]

        # Some course credits end with a space
        if courseCreditStr[-1:] == " ":
            courseCreditStr = courseCreditStr[:-1]

        # Some end with " (", sometimes the case if it is open to 8th graders
        if courseCreditStr[-2:] == " (":
            courseCreditStr = courseCreditStr[:-2]
    else:
        courseCreditStr = "Math"

    courseDescElements: list[bs4.PageElement] = []

    if brInsideStrong:
        courseDescElements = list(titleTag.next_siblings)
    else:
        brTag: bs4.Tag | bs4.NavigableString | None = titleTag.findNextSibling(name="br")
        if brTag != None:
            courseDescElements = list(brTag.next_siblings)
        # Otherwise, the course should have no description, so courseDescTags is left empty, as is courseDesc

    for thisCourseDescElement in courseDescElements:
        if type(thisCourseDescElement) == bs4.NavigableString:
            courseDesc += thisCourseDescElement
        elif type(thisCourseDescElement) == bs4.Tag:
            thisCourseDescElementStr: str | None = thisCourseDescElement.string
            if thisCourseDescElementStr != None:
                courseDesc += thisCourseDescElementStr

    # How do you even manage to put an invisible character at the end of a course description
    if courseDesc[-1:] == " ":
        courseDesc = courseDesc[:-1]
    
    courseCredits: list[str]
    courseLevel: str | None
    if courseCreditStr == "Foreign Language":
        courseCredits = ["Foreign Language"]
        courseLevel = parseCourseLevel(courseTitle)
    else:
        courseCredits, courseLevel = parseCourseCreditStr(courseCreditStr)
    
    # Some courses are repeated across categories; some with different credit types, so we have to merge them
    for otherCourseDict in courseDicts:
        if otherCourseDict[COURSES_TITLE_KEY] == courseTitle:
            otherCourseDict[COURSES_CREDITS_KEY] = sorted(set(courseCredits + otherCourseDict[COURSES_CREDITS_KEY])) # type: ignore
            return None
    
    courseCredits = sorted(courseCredits)

    return {COURSES_TITLE_KEY: courseTitle,
            COURSES_CREDITS_KEY: courseCredits,
            COURSES_LEVEL_KEY: courseLevel,
            COURSES_DESC_KEY: courseDesc}

titleTags: Final[bs4.ResultSet[bs4.Tag]] = catalogSoup.find_all("strong")

# One strong tag is an empty whitespace in the middle of the course catalog and should not be there
for tagIndex, thisTag in enumerate(titleTags):
    if thisTag.string == " ":
        del(titleTags[tagIndex])

for thisTitleTag in titleTags:
    courseDict: dict[str, str | None | list[str]] | None = getCourseInfo(thisTitleTag)
    if courseDict != None:
        courseDicts.append(courseDict)

courseDF: pd.DataFrame = pd.DataFrame(courseDicts)
courseDF = courseDF.set_index(COURSES_TITLE_KEY)
courseDF.to_csv("courses.csv")
