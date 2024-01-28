from enum import Enum
from django.db import models


class Day(Enum):
    monday = "MONDAY"
    tuesday = "TUESDAY"
    wednessday = "WEDNESSDAY"
    thursday = "THURSDAY"
    friday = "FRIDAY"
    saturday = "SATURDAY"
    sunday = "SUNDAY"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
    
class TimetableEntries(models.Model):
    day = models.CharField(max_length=255, choices=Day.choices())
    date = models.DateField()
    timeslot = models.CharField(max_length=50, null=False)
    building = models.CharField(max_length=255, null=False)
    room = models.CharField(max_length=255, null=False)
    course_code = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UploadedTimetable(models.Model):
    name = models.CharField()
    hidden = models.BooleanField(null=False, default=False)
    timetable_entry = models.ForeignKey(TimetableEntries, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

