from django.db import models

# Create your models here.
FALL = "F"
SPRING = "S"
SEMESTER_CHOICES = {
    FALL: "Fall",
    SPRING: "Spring"
}

FRESHMAN = "FR"
SOPHOMORE = "SO"
JUNIOR = "JR"
SENIOR = "SR"
GRADUATE = "GR"
YEAR_IN_SCHOOL_CHOICES = {
    FRESHMAN: "Freshman",
    SOPHOMORE: "Sophomore",
    JUNIOR: "Junior",
    SENIOR: "Senior",
    GRADUATE: "Graduate",
}

class Room(models.Model):
    building = models.CharField(max_length=5)
    room_number = models.IntegerField()
    capacity = models.IntegerField()

class Day(models.Model):
    MON = "Mon"
    TUE = "Tues"
    WED = "Wed"
    THU = "Thu"
    FRI = "FRI"
    DAY_OF_WEEK_CHOICES = {
        MON: "Monday",
        TUE: "Tuesday",
        WED: "Wednesday",
        THU: "Thursday",
        FRI: "Friday",
    }
    day_of_week = models.CharField(
        max_length=3,
        choices=DAY_OF_WEEK_CHOICES,
        default=MON,
    )
    
class Course(models.Model):
    subject = models.CharField(max_length=5)
    classNumber = models.IntegerField()
    prerequisites = models.ManyToManyField('self')
    equivalent_courses = models.ManyToManyField('self')
    same_semester_courses = models.ManyToManyField('self')
    credits = models.IntegerField()
    weight = models.IntegerField()
    
   
class Schedule(models.Model):
    year = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )
    semester = models.CharField(
        max_length=1,
        choices=SEMESTER_CHOICES,
        default=FALL,
    )

 
class Section(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    section_id = models.IntegerField()
    professor = models.CharField(max_length=255)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    days = models.ManyToManyField(Day)
    room = models.ForeignKey(Room, on_delete = models.SET_NULL)
    schdule = models.ForeignKey(Schedule, on_delete = models.CASCADE)
    
class PlanSemester(models.Model):
    year = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )
    semester = models.CharField(
        max_length=1,
        choices=SEMESTER_CHOICES,
        default=FALL,
    )
    courses = models.ManyToManyField(Course)
    ...
    
class Change(models.Model):
    section = models.ForeignKey(Course, on_delete = models.CASCADE)
    new_start_time = models.IntegerField()
    new_end_time = models.IntegerField()
    new_days = models.ManyToManyField(Day)
    new_room = models.ForeignKey(Room, on_delete = models.SET_NULL)
    ...
    
class Conflict(models.Model):
    sectionA = models.ForeignKey(Section, on_delete = models.CASCADE)
    sectionB = models.ForeignKey(Section, on_delete = models.CASCADE)
    ...
    
from django.db import models

class FilteredUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    filtered_data = models.JSONField()
    uploaded_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
