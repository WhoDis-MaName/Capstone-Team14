from django.http import JsonResponse, FileResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import clingo
import re
import json
import os
from ..models import FilteredUpload


@csrf_exempt
def optimize_schedule(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not asp_filename or not default_storage.exists(asp_filename):
            return JsonResponse({"error": "ASP file not found in session"}, status=404)

        # Define paths
        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_path = os.path.join(root_dir, "media", asp_filename)
        minimizer_path = os.path.join(root_dir, "clingo", "overlap_minimizer.lp")

        # Temporary file path (output.json)
        temp_output_path = os.path.join(root_dir, "media", "output.json")

        # == Clingo Application Definition ==
        class ClingoApp(clingo.application.Application):
            def main(self, ctl, files):
                ctl.load(asp_path)
                ctl.load(minimizer_path)
                ctl.ground()
                ctl.solve()

            def print_model(self, model, printer):
                symbols = [str(s) for s in model.symbols(shown=True)]
                convert_to_json(symbols, temp_output_path)

        # == Supporting JSON Conversion Functions ==
        def convert_time(t):
            t = int(t)
            hours = t // 60
            minutes = t % 60
            suffix = "AM" if hours < 12 else "PM"
            hours = hours if hours <= 12 else hours - 12
            return f"{hours}:{minutes:02d}{suffix}"

        def parse_line(line):
            match = re.match(r"scheduled_section\((.*?)\)", line.strip())
            if not match:
                return None
            fields = match.group(1).split(",")
            if len(fields) != 8:
                return None
            (
                subject_course,
                section,
                class_number,
                start,
                end,
                days,
                location,
                instructor,
            ) = fields
            subject = subject_course[:4].upper()
            course_number = subject_course[4:]
            section = section[1:]
            class_number = class_number[1:]
            time_str = f"{convert_time(start)} - {convert_time(end)}"
            return (
                subject,
                course_number,
                section,
                {
                    "Class Number": class_number,
                    "Date": "Aug 26, 2024 - Dec 20, 2024",
                    "Time": time_str,
                    "Days": days.upper(),
                    "Location": location.replace("_", " ").title(),
                    "Instructor": instructor.replace("_", " ").title(),
                },
            )

        def convert_to_json(symbols, output_file):
            data = {}
            for line in symbols:
                parsed = parse_line(line)
                if not parsed:
                    continue
                subject, course_number, section, section_data = parsed
                if subject not in data:
                    data[subject] = {}
                if course_number not in data[subject]:
                    data[subject][course_number] = {
                        "title": "TBD",
                        "desc": "TBD",
                        "prereq": "-",
                        "sections": {},
                    }
                data[subject][course_number]["sections"][section] = section_data

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

        # == Run Clingo App ==
        clingo.application.clingo_main(ClingoApp())

        # == Save File via Django ==
        with open(temp_output_path, "r") as f:
            optimized_data = json.load(f)

        upload_count = FilteredUpload.objects.count() + 1
        optimized_filename = f"uploads/optimized_output{upload_count}.json"
        saved_path = default_storage.save(
            optimized_filename, ContentFile(json.dumps(optimized_data, indent=2))
        )

        # Optionally attach to latest upload
        try:
            latest_record = FilteredUpload.objects.latest("uploaded_at")
            latest_record.optimized_file.save(
                os.path.basename(saved_path),
                ContentFile(json.dumps(optimized_data, indent=2)),
            )
        except FilteredUpload.DoesNotExist:
            pass  # If no uploads yet, silently continue

        return JsonResponse(
            {
                "status": "success",
                "message": "Optimization complete.",
                "optimized_file": saved_path,
                "optimized_data": optimized_data,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
