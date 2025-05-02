import os
import sys

from django.apps import AppConfig
from django.conf import settings


class SchedulefunctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduleFunctions'
    
    def ready(self):
        if not os.path.exists(os.path.join(settings.BASE_DIR, "run_once.lock"))  and not any(flag in sys.argv for flag in ['makemigrations', 'migrate']):
            # Code to run once on startup
            print("Startup code executed")
            
            from .data_processing.get_four_year import read_four_year
            from .data_processing.get_requirements import process_degree_requirements
            from .data_processing.process_four_year import create_constraints
            from .to_database import store_requirements, store_plan
            import json
            
            # Four Year Plan
            if os.name == 'nt':
                current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
            else:
                current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
                

            path = current_directory.split(os.sep)

            root_index = path.index('Capstone-Team14')
            root_dir = os.sep.join(path[:root_index+1])
            data_dir = os.path.join(root_dir, 'data_files')
            
            try:
                os.makedirs(data_dir)
            except:
                pass
            plan_file = os.path.join(data_dir,'four_year_plan','four_year_plan.json')
            url = 'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/#fouryearplantext'
            read_four_year(url, plan_file)
            constraints = create_constraints(plan_file)
            plan_file = os.path.join(data_dir,'four_year_plan','fouryearplan_processed.json')
            with open(plan_file, 'w') as f:
                json.dump(constraints,f, indent=4)
            
            requirements_file = os.path.join(data_dir,'requirements','requirements.json')
            try:
                os.makedirs(os.path.join(data_dir,'requirements'))
            except:
                pass
            urls = [
                'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/artificialintelligence-concentraton/',
                'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/game-programming-concentration/',
                'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/internet-technologies-it-concentration-computer-science-majors/',
                'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/information-assurance-concentration/',
                'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/software-engineering-concentration/'
            ]
            process_degree_requirements(urls, requirements_file)
            
            store_requirements(requirements_file)
            store_plan(plan_file)
            with open("run_once.lock", "w") as f:
                f.write("Run once")
            settings.STARTUP_DONE = True
        ...

