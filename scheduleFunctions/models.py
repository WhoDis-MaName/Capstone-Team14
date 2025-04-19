from django.db import models

# Create your models here.
class Room(models.Model):
    building = models.CharField(max_length=255)
    room_number = models.IntegerField()
    capacity = models.IntegerField()
    
    def print_clingo(self) -> str:
        # peter_kiewit_institute_157
        return "_".join(self.building.split(" ").append(self.room_number))
        ...

class Day(models.Model):
    MON = "m"
    TUE = "t"
    WED = "w"
    THU = "r"
    FRI = "f"
    DAY_OF_WEEK_CHOICES = {
        MON: "Monday",
        TUE: "Tuesday",
        WED: "Wednesday",
        THU: "Thursday",
        FRI: "Friday",
    }
    day_of_week = models.CharField(
        max_length=4,
        choices=DAY_OF_WEEK_CHOICES,
        default=MON,
    )
    def print_clingo(self) -> str:
        inverse_choices = {value:key for key, value in self.DAY_OF_WEEK_CHOICES}
        return inverse_choices[self.day_of_week]
        ...


class Course(models.Model):
    subject = models.CharField(max_length=5)
    class_number = models.IntegerField()
    name = models.CharField(max_length=255)
    prerequisites = models.ManyToManyField('self')
    equivalent_courses = models.ManyToManyField('self')
    same_semester_courses = models.ManyToManyField('self')
    credits = models.IntegerField()
    weight = models.IntegerField()
    def print_clingo(self) -> str:
        ...
    
class Requirement(models.Model):
    major_label = models.CharField(max_length=255)
    requirement_label = models.CharField(max_length=255)
    total_credits = models.IntegerField()
    course_options = models.ManyToManyField(Course)
    def print_clingo(self) -> str:
        ...
 
class Section(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    section_number = models.IntegerField()
    section_id = models.IntegerField(primary_key=True)
    professor = models.CharField(max_length=255)
    start_time = models.TimeField(auto_now=False)
    end_time = models.TimeField(auto_now=False)
    days = models.ManyToManyField(Day)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    
    def print_dashboard(self) -> str:
        text = f'{self.course.subject} {self.course.class_number} - {self.course.name} ({"/".join(self.days)} {self.start_time.strftime("%I:%M%p")} - {self.end_time.strftime("%I:%M%p")})'
        return text
    
    def print_clingo(self) -> str:
        # section(cist1010, s001, c15257, 570, 620, t, peter_kiewit_institute_157, farida_majid).
        self_text = f'section('        
        + f'{self.course.subject}{self.course.class_number}'
        + f', s{self.section_id}, c{self.course.course_id}'
        + f', {self.start_time.hour * 60 + self.start_time.minute}, {self.end_time.hour * 60 + self.end_time.minute}'
        + f', {"".join([day.print_clingo() for day in self.days])}'       
        + f', {self.room.print_clingo()}'       
        + f', {self.professor.replace(" ", "_")}'        
        + ').'
                
        
        return '\n'.join([self_text])
        ...
        

    
class PlanSemester(models.Model):
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
    new_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    ...
    
class Conflict(models.Model):
    sectionA = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='conflicts_as_A')
    sectionB = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='conflicts_as_B')
    ...
    
from django.db import models

class FilteredUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)  # This will store the original uploaded filename
    filtered_data = models.JSONField()
    non_filtered_data = models.JSONField()
    uploaded_file = models.FileField(upload_to='uploads/')  # Raw input file

    # Optional: Add these new fields to store the saved file paths
    raw_file_path = models.CharField(max_length=255, blank=True)
    filtered_file_path = models.CharField(max_length=255, blank=True)
    remaining_file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
