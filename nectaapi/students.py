"""
A list of all students with their performance in a particular school or center
returns a dictionary
school_name, school_number, number_of_students, year_of_exam, exam_type, students[
    {
        examination_number,
        gender,
        division,
        points,
        subjects:{
            subject1:score1,
            subject2:score2,
            ...
        }
    }
    ...
]
"""

import requests
from nectaapi import summary
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from nectaapi.model import StudentsModel


def students(year: int, exam_type: str, school_number: str) -> Optional[Dict[str, Any]]:
    """Get all students with their performance in a particular school or center

    Args:
        year(int),exam_type(str), school_number(str)

    Returns:
        Dict
    """
    student = StudentsModel(year=year, exam_type=exam_type, school_number=school_number)
    exam_type = student.exam_type.lower()
    school_number = student.school_number.lower()
    year = int(student.year)

    index = student.index
    url = student.get_summary_url()

    if url is None:
        return None

    data = requests.get(url)
    soup = BeautifulSoup(data.text, "html.parser")

    if data.status_code != 200:
        raise Exception(f"failed to connect to server\nError code {data.status_code}")
    else:
        # get some data from summary function
        school_summary = summary.summary(year, exam_type, school_number)

        students = {
            "school_number": school_number,
            "school_name": school_summary["school_name"],
            "year_of_exam": year,
            "exam_type": exam_type,
            "number_of_students": school_summary["number_of_students"],
            "students": [],
        }

        student_data = scrapStudents(soup, index)
        students["students"] = student_data

        return students


def scrapStudents(soup, index) -> List[Dict[str, Any]]:
    studentsTable = soup.find_all("table")[index]
    data = []

    for tr in studentsTable.find_all("tr")[1:]:
        row = []
        for td in tr.find_all("td"):
            row.append(td.text.strip("\n"))

        subjects = splitAfter(row[4])
        student = {
            "examination_number": row[0],
            "gender": row[1],
            "division": row[3],
            "points": row[2],
            "subjects": subjects,
        }

        data.append(student)

    return data


# assisting function in obtaining a dictionary of candidates subjects and grades
def splitAfter(text) -> Dict[str, str]:
    subjects = {}  # a dictionary of subject grade pair
    values = []
    temp = ""
    for i in range(0, len(text) - 1):
        temp += text[i]
        if text[i] == "'" and text[i + 1] == " ":
            values.append(temp)
            temp = ""

    for v in values:
        q = v.split("-")
        subject = q[0].strip()
        grade = q[1].strip().strip("'")
        subjects.update({subject: grade})

    return subjects
