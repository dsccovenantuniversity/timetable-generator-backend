from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz
from fastapi.responses import FileResponse
from openpyxl import Workbook
from typing import List, Dict
import re
import pandas as pd
import json
from io import BytesIO
app = FastAPI()


class CourseScheduleItem(BaseModel):
    course: str
    Building: str
    Room: str
    Time: str
    Day: str


class TimetableResponse(BaseModel):
    message: str

#  response_model=TimetableResponse


@app.post('/upload_course_reg/')
async def upload_course_reg(file: UploadFile = File(...)):
    try:

        pdf_content = await file.read()
        course_codes = extract_course_codes_from_pdf(pdf_content)

        return {'course_codes': course_codes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_course_codes_from_pdf(pdf_content):

    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page_number in range(doc.page_count):
        page = doc[page_number]
        text += page.get_text("text")

    course_codes = parse_course_codes_from_text(text)
    return course_codes


def parse_course_codes_from_text(text):

    course_code_pattern = re.compile(r'\b[A-Z]{3}\d{3}\b')
    course_codes = course_code_pattern.findall(text)
    return course_codes


@app.post('/create_class_timetable/')
def create_class_timetable(offered_courses: List[str]):
    monday_timetable = pd.read_csv('timetable/monday.csv')
    tuesday_timetable = pd.read_csv('timetable/tuesday.csv')
    wednesday_timetable = pd.read_csv('timetable/wednesday.csv')
    thursday_timetable = pd.read_csv('timetable/thursday.csv')
    friday_timetable = pd.read_csv('timetable/friday.csv')
    timetable_list = [monday_timetable, tuesday_timetable,
                      wednesday_timetable, thursday_timetable, friday_timetable]
    found_courses = {}

    timetable_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for ind, timetable in enumerate(timetable_list):
        for index, row in timetable.iterrows():
            for col in timetable.columns[2:]:
                if '_' in col:
                    time_slot = col.split('_')
                    start_time, end_time = time_slot[0], time_slot[1]
                else:
                    start_time, end_time = None, None

                subjects = str(row[col]).split(
                    '/') if pd.notna(row[col]) else []
                for subject in subjects:
                    if subject.strip() in offered_courses:
                        course_key = subject.strip()
                        if course_key not in found_courses:
                            found_courses[course_key] = []
                        found_courses[course_key].append({
                            "course": subject,
                            "Building": row.iloc[0],
                            "Room": row.iloc[1],
                            "Time": f"{start_time}-{end_time}" if start_time and end_time else None,
                            "Day": timetable_name[ind]}
                        )

    return found_courses


@app.post("/generate_timetable/")
def generate_timetable(schedule: Dict[str, List[Dict[str, str]]]):

    timetable_df = pd.DataFrame(index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                columns=['8am-9am', '9am-10am', '10am-11am', '11am-12noon', '12noon-1pm',
                                         '1pm-2pm', '2pm-3pm', '3pm-4pm', '4pm-5pm', '5pm-6pm'])

    for course, details_list in schedule.items():
        for details in details_list:
            day = details.get('Day')
            time = details.get('Time')
            if day and time:
                timetable_df.loc[day, time] = course
    for day in timetable_df.index:
        timetable_df.loc[day, '2pm-3pm'] = "BREAK TIME"

    excel_filename = "timetable.xlsx"
    timetable_df.to_excel(excel_filename)

    return FileResponse(excel_filename, filename="timetable.xlsx")

# WORK ON EXCEL
# DEPLOY
# TEST WITH A RANDOM APPLICATION
