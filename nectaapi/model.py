import re
from typing import List, Union, Optional
from pydantic import BaseModel, validator
from urllib.parse import urlparse


class NectaBase(BaseModel):
    year: Union[int, str]
    exam_type: str

    # emum = ["acsee", "csee"]

    @validator("year")
    def year_must_be_greater_than_2005(cls, value):
        if int(value) < 2005:
            raise ValueError("year must be greater than 2000")
        return int(value)

    @validator("exam_type")
    def exam_type_must_be_valid(cls, value):
        if value.lower() not in ["acsee", "csee"]:
            raise ValueError("exam_type must be either acsee or csee")
        return value

    def get_school_url(self):
        """Returns school request url

        Args:
            year(int),exam_type(str), school_number(str)

        Returns:
            str
        """
        url = ""

        exam_type = self.exam_type
        year = self.year

        if self.exam_type == "csee":
            if year == 2022:
                url = "https://onlinesys.necta.go.tz/results/2022/csee/index.htm"
            elif year == 2016:
                url = f"https://onlinesys.necta.go.tz/results/{year}/csee/index.htm"
            else:
                url = f"https://onlinesys.necta.go.tz/results/{year}/csee/csee.htm"

        elif exam_type == "acsee":
            if year == 2023:
                url = "https://matokeo.necta.go.tz/results/2023/acsee/index.htm"
            elif year > 2019:
                url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/index.htm"
            elif year == 2014:
                url = f"https://onlinesys.necta.go.tz/results/2014/acsee/"
            else:
                url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/acsee.htm"
        else:
            # will never reach this point though
            raise ValueError("exam_type must be either acsee or csee")
        return urlparse(url).geturl()


class StudentsModel(NectaBase):
    school_number: str

    @validator("school_number")
    def school_number_must_be_valid(cls, value: str):
        pattern = re.compile(r"^[sS][0-9]{4}$|^[pP][0-9]{4}$")
        if not pattern.match(value):
            raise ValueError("school_number must be in the format of sxxx or Pxxx")
        return value

    @property
    def index(self):
        if self.exam_type == "csee":
            return (
                (1 if self.year > 2019 else 0)
                if self.school_number.lower().startswith("p")
                else (2 if self.year > 2019 else 0)
            )

        else:
            # Complex a bit
            return (
                (1 if self.year > 2018 else 0)
                if self.school_number.startswith("p")
                else (2 if self.year > 2018 else 0)
            )

    def get_summary_url(self) -> Optional[str]:
        """Get summary/student request url

        Args:
            year(int),exam_type(str), school_number(str)

        Returns:
            parsed url or None
        """
        url = ""

        exam_type = self.exam_type
        school_number = self.school_number
        year = int(self.year)

        if exam_type == "acsee":
            if year == 2023:
                url = f"https://matokeo.necta.go.tz/results/2023/acsee/results/{school_number}.htm"
            elif year > 2014 and year < 2023:
                url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/results/{school_number}.htm"
            elif year < 2015 and year > 2005 and year != 2008:
                url = f"https://maktaba.tetea.org/exam-results/{exam_type.upper()}{year}/{school_number}.html"
            else:
                return None

        elif exam_type == "csee":
            if int(year) > 2014:
                url = f"https://onlinesys.necta.go.tz/results/{year}/csee/results/{school_number}.htm"
            else:
                url = f"https://onlinesys.necta.go.tz/results/{year}/csee/{school_number}.htm"
        return urlparse(url).geturl()
