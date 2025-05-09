from django.db import models

# Create your models here.
class Room(models.Model):
    building = models.CharField(max_length=255)
    room_number = models.IntegerField()
    capacity = models.IntegerField(default=30)
    
    def print_clingo(self) -> str:
        # peter_kiewit_institute_157
        try:
            return "_".join(self.building.lower().split(" ").append(self.room_number))
        except TypeError:
            return "_".join([self.building.lower(),str(self.room_number)])
        ...
    @classmethod
    def print_all_clingo(cls):
        room_list = []
        for room in cls.objects.all():
            room_list.append(room.print_clingo())
        text = 'room(' + ';'.join(room_list) + ').'
        return text

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
        inverse_choices = {value:key for key, value in self.DAY_OF_WEEK_CHOICES.items()}
        return inverse_choices[self.day_of_week]
        ...
    def __str__(self):
        return self.day_of_week


class Course(models.Model):
    # course(csci2240, "intro_to_c_programming", "_").
    subject = models.CharField(max_length=5)
    class_number = models.IntegerField()
    name = models.CharField(max_length=255)
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='required_for')
    equivalent_courses = models.ManyToManyField('self', symmetrical=True)
    same_semester_courses = models.ManyToManyField('self', symmetrical=True)
    credits = models.IntegerField(null=True)
    weight = models.IntegerField()
    def print_clingo(self) -> str:
        self_text = ''
        if self.subject in ['CSCI']:
            self_text = 'course('
            
        else:
            self_text = 'non_cs_course('
        
        year = self.class_number // 1000
        if year > 4:
            year = 5
            
        self_text = ''.join([self_text,
            f'{self.subject.lower()}{self.class_number}',
            f', "{self.name.replace(" ", "_").replace("-", "_").replace(".", "").lower()}", "_").'])
        weight_text = ''.join([f'course_weight({self.subject.lower()}{self.class_number}',
            f',{self.weight},{year}).'])
        
        return {'self': self_text, 'weight': weight_text}
        ...
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subject', 'class_number'], name='unique_course_code')
        ]
    
    @classmethod
    def print_non_cs(cls):
        course_list = []
        for course in cls.objects.exclude(subject__in=['CSCI']):
            course_list.append(f'{course.subject.lower()}{course.class_number}')
        text = 'non_cs_class(' + ';'.join(course_list) + ').'
        return text
    
class Requirement(models.Model):
    major_label = models.CharField(max_length=255)
    requirement_label = models.CharField(max_length=255)
    total_credits = models.IntegerField()
    course_options = models.ManyToManyField(Course)
    
    def print_clingo(self) -> str:
        
        ...
 
class Proffessor(models.Model):
    name = models.CharField(max_length=255)
    
    def print_clingo(self) -> str:
        return self.name.replace(" ", "_").replace("-", "_").replace(".", "").lower()
    
    @classmethod
    def print_all_clingo(cls):
        prof_list = []
        for prof in cls.objects.all():
            prof_list.append(prof.print_clingo())
        text = 'professor(' + ';'.join(prof_list) + ').'
        return text
class TimeSlot(models.Model):
    start_time = models.TimeField(auto_now=False)
    end_time = models.TimeField(auto_now=False)
    days = models.ManyToManyField(Day)
    credits = models.IntegerField()
    
    def print_clingo(self) -> str:
        self_text = f'time_slot_credits({self.start_time.hour * 60 + self.start_time.minute}, {self.end_time.hour * 60 + self.end_time.minute}, {"".join([day.print_clingo() for day in self.days.all()])}, {self.credits}).'
        
        return {'self': self_text}
    
    
class Section(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    section_number = models.IntegerField()
    section_id = models.IntegerField()
    professor = models.ForeignKey(Proffessor, on_delete = models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete = models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    changed = models.BooleanField(default=False)    
    
    def print_clingo(self) -> str:
        # section(cist1010, s001, c15257, 570, 620, t, peter_kiewit_institute_157, farida_majid).
        if self.course.subject in ['CSCI']:
            self_text = 'section('
            
        else:
            self_text = 'non_cs_section('   
        self_text = ''.join([self_text,     
            f'{self.course.subject.lower()}{self.course.class_number}',
            f', s{self.section_number}, c{self.section_id}',
            f', {self.time_slot.start_time.hour * 60 + self.time_slot.start_time.minute}',
            f', {self.time_slot.end_time.hour * 60 + self.time_slot.end_time.minute}',
            f', {"".join([day.print_clingo() for day in self.time_slot.days.all()])}',       
            f', {self.room.print_clingo()}',
            f', {self.professor.print_clingo()}',        
            ').'])
        section_count = Section.objects.filter(course=self.course).count()
        critical_text = ''
        if section_count == 1:
            critical_text = f'critical_section({self.course.subject.lower()}{self.course.class_number}, c{self.section_id}).'
        time_slot_text = ''
        if self.course.subject in ['CSCI']:
            time_slot_text = 'time_slot('
        else:
            time_slot_text = 'non_cs_time_slot('
            
        time_slot_text = ''.join([time_slot_text,
            f', {self.time_slot.start_time.hour * 60 + self.time_slot.start_time.minute}',
            f', {self.time_slot.end_time.hour * 60 + self.time_slot.end_time.minute}',
            f', {"".join([day.print_clingo() for day in self.time_slot.days.all()])}',
            ').'])
        
        return {'self': self_text,'critical': critical_text, 'time_slot': time_slot_text}
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
    
# class Change(models.Model):
#     section = models.ForeignKey(Course, on_delete = models.CASCADE)
#     old_time = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)
#     new_time = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)
#     old_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
#     new_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
#     ...
    
# class Conflict(models.Model):
#     sectionA = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='conflicts_as_A')
#     sectionB = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='conflicts_as_B')
#     ...
    
from django.db import models

class FilteredUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    filtered_data = models.JSONField()
    non_filtered_data = models.JSONField()
    uploaded_file = models.FileField(upload_to='uploads/')  # Raw input file

    # Previously saved file paths
    raw_file_path = models.CharField(max_length=255, blank=True)
    filtered_file_path = models.CharField(max_length=255, blank=True)
    remaining_file_path = models.CharField(max_length=255, blank=True)

    # ✅ New field to store the optimized output file
    optimized_file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
