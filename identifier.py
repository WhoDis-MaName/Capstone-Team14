import sys, clingo, math
from jsonconverter import convert
import argparse

parser = argparse.ArgumentParser(description="Input class json")

# Add arguments with default values
parser.add_argument(
    "--file", type=str, default="filtered.json", help="File name to process"
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
