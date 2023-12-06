from fastapi import FastAPI, Path
from typing import List

import pandas as pd
import json
app = FastAPI()


@app.post('/create_class_timetable/')
def create_class_timetable(offered_courses: List[str] = Path(None, "A list of the courses the student is offering", gt=2)):
    monday_timetable = pd.read_csv('timetable/monday.csv')
    tuesday_timetable = pd.read_csv('timetable/tuesday.csv')
    wednesday_timetable = pd.read_csv('timetable/wednesday.csv')
    thursday_timetable = pd.read_csv('timetable/thursday.csv')
    friday_timetable = pd.read_csv('timetable/friday.csv')
    timetable_list = [monday_timetable, tuesday_timetable,
                      wednesday_timetable, thursday_timetable, friday_timetable]
    found_courses = []

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
                        found_courses.append({
                            "course": subject,
                            "Building": row.iloc[0],
                            "Room": row.iloc[1],
                            'Time': f"{start_time}-{end_time}" if start_time and end_time else None,
                            'Day': timetable_name[ind]



                        })

    return json.dumps(found_courses, indent=2)
