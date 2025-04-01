import json
from datetime import datetime
from django.core.management.base import BaseCommand
from scheduleFunctions.models import FilteredUpload

class Command(BaseCommand):
    help = "Convert the latest uploaded JSON file to ASP facts"

    def convert24(self, time):
        t = datetime.strptime(time, "%I:%M%p")
        return t.hour * 60 + t.minute

    def convert(self, file):
        with open(file, "r") as f:
            data = json.load(f)

        facts = []
        classes = set()
        rooms = set()
        professors = set()
        times = set()

        for term, subjects in data.items():
            for subject, courses in subjects.items():
                for course_num, course_info in courses.items():
                    course_id = (
                        f"{subject}{course_num}".lower()
                        .replace(" ", "_")
                        .replace(".", "")
                        .replace("-", "_")
                    )
                    title = (
                        course_info.get("title", "")
                        .lower()
                        .replace(" ", "_")
                        .replace(".", "")
                        .replace("-", "_")
                    )
                    prereq = (
                        course_info.get("prereq", "none")
                        .lower()
                        .replace(" ", "_")
                        .replace("-", "none")
                        .replace(".", "")
                        .replace("-", "_")
                    )

                    facts.append(f'course({course_id}, "{title}", {prereq}).')
                    classes.add(course_id)

                    for section_num, section_info in course_info.get("sections", {}).items():
                        section_num = "s" + section_num.lower()
                        class_number = (
                            "c" + section_info.get("Class Number", "").split()[0].lower()
                        )

                        time = section_info.get("Time", "TBA")
                        if time == "TBA":
                            start, end = "tba", "tba"
                        else:
                            start, end = time.split(" - ")
                            start = self.convert24(start)
                            end = self.convert24(end)

                        days = (
                            section_info.get("Days", "TBA")
                            .strip()
                            .lower()
                            .replace(" ", "_")
                            .replace("-", "_")
                        )
                        location = (
                            section_info.get("Location", "Unknown")
                            .lower()
                            .replace(" ", "_")
                            .replace(".", "")
                            .replace("-", "_")
                        )
                        instructor = (
                            section_info.get("Instructor", "Unknown")
                            .lower()
                            .replace(" ", "_")
                            .replace(".", "")
                            .replace("-", "_")
                        )
                        if location == "totally_online" or location == "to_be_announced" or start == "tba":
                            continue

                        facts.append(
                            f"section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor})."
                        )

                        rooms.add(location)
                        professors.add(instructor)
                        if start != "tba" and end != "tba" and days != "tba":
                            times.add(f"time_slot({start}, {end}, {days}).")

        facts.append(f"class({'; '.join(classes)}).")
        facts.append(f"room({'; '.join(rooms)}).")
        facts.append(f"professor({'; '.join(professors)}).")
        facts.extend(times)

        asp_filename = file.replace(".json", ".lp")
        with open(asp_filename, "w") as f:
            f.write("\n".join(facts))

        self.stdout.write(self.style.SUCCESS(f"ASP facts written to {asp_filename}"))

    def handle(self, *args, **kwargs):
        latest = FilteredUpload.objects.latest('uploaded_at')
        file_path = latest.uploaded_file.path
        self.convert(file_path)
