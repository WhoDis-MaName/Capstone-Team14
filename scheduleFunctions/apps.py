import os

from django.apps import AppConfig
from .data_processing.get_four_year import read_four_year


class SchedulefunctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduleFunctions'
    
    def ready(self):
        
        # Four Year Plan
        if os.name == 'nt':
            current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
        else:
            current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
            

        path = current_directory.split(os.sep)

        root_index = path.index('Capstone-Team14')
        root_dir = os.sep.join(path[:root_index+1])
        data_dir = os.path.join(root_dir, 'data_files', 'four_year_plan')
        
        try:
            os.makedirs(data_dir)
        except:
            pass
        filename = os.path.join(data_dir,'fourYearPlan.json')
        url = 'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/#fouryearplantext'
        read_four_year(url, filename)
        
        
        ...
