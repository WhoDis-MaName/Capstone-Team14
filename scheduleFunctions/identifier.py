import sys, clingo, math
from clingo.jsonconverter import convert
import argparse
import os

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
path = current_directory.split(os.sep)

root_index = path.index('scheduleFunctions')
root_dir = os.sep.join(path[:root_index+1])
read_dir = os.path.join(root_dir, 'data_files', 'uploaded_schedule')

parser = argparse.ArgumentParser(description="Input class json")

# Add arguments with default values
parser.add_argument(
    "--file", type=str, default=os.path.join(read_dir, "filtered.json"), help="File name to process"
)


class ClingoApp(clingo.application.Application):
    def main(self, ctl, files):

        args = parser.parse_args()

        # Access the arguments
        file = args.file
        print(file)
        # TODO: Update to work with input file not just hard coded file
        convert(file)
        ctl.load("identifyconflict.lp")

        ctl.ground()
        ctl.solve()

    # def print_model(self, model, printer) -> None:
    #     board = Sudoku({}).from_model(model)
    #     print(board)


clingo.application.clingo_main(ClingoApp())
