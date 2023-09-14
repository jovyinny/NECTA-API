'''
A list of all schools and their registration numbers in a given year and exam type

return format
type: dictionary
example: {
    "exam_type":"",
    "year_of_exam":"",
    "number_of_schools":"",
    "schools":[
        {"school_name":"school name 1", "school_number":"school number 1"},
        {"school_name":"school name 2", "school_number":"school number 2"},
        ...
    ]
}
'''
from bs4 import BeautifulSoup
import requests
from typing import Dict,Any

def schools(year:int, exam_type:str)->Dict[str,Any]:
    """Gets all schools and their registration numbers in a given year and exam type

    Args:
        year(int),exam_type(str)
    
    Returns:
        Dict
    """
    
    url = ""

    # the number of waste rows to skip (letters in the home page), if available
    skip = 0
    year=int(year)
    exam_type = exam_type.lower()

    if exam_type == "csee":
        if year==2022:
            url="https://onlinesys.necta.go.tz/results/2022/csee/index.htm"
        elif year == 2016:
            url = f"https://onlinesys.necta.go.tz/results/{year}/csee/index.htm" 
        else:
            url = f"https://onlinesys.necta.go.tz/results/{year}/csee/csee.htm" 

        if year > 2014:
            skip = 28

    elif exam_type == "acsee":
        if year == 2023:
            url="https://matokeo.necta.go.tz/results/2023/acsee/index.htm"
        elif year > 2019:
            url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/index.htm" 
        elif year == 2014:
            url = f"https://onlinesys.necta.go.tz/results/2014/acsee/" 
        else:
            url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/acsee.htm" 

        if year > 2015:
            skip = 27
    else:
        # invalid exam type
        raise Exception(f"Invalid Exam Type {exam_type}")

    data = requests.get(url)
    if data.status_code == 200:
        soup = BeautifulSoup(data.text, 'html.parser')

        # a list of dictionaries to hold school's registration number and name
        schools = []

        # get all the data present in the tables i.e list of all schools and centers
        for font in soup.find_all('font'):
            for a in font.find_all('a'):
                clean = a.text.strip('\n\r')
                school = clean.split(' ')

                school_name = ""
                for s in school[1:]:
                    school_name = f"{school_name} {s}"

                schools.append({"school_name": school_name, "school_number":school[0]})

        # eliminate initial dirt, the first letters that were extracted as school names
        schools = schools[skip:]

        schools_data = {
            "exam_type": exam_type,
            "year_of_exam": year,
            "number_of_schools": len(schools),
            "description": f"a list of all schools and centers that participated in {exam_type} in {year}",
            "schools": schools            
        }

        # return a dictionary of all schools and more info
        return schools_data
    else:
        # upon error return raise an exception
        raise Exception(f"Failed to access {url}\nResponse code: {data.status_code}")