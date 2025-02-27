import sys, clingo, math
from jsonconverter import convert


class ClingoApp(clingo.application.Application):
    def main(self, ctl, files):

        # TODO: Update to work with input file not just hard coded file
        convert("filtered.json")
        ctl.load("identifyconflict.lp")

        ctl.ground()
        ctl.solve()

    # def print_model(self, model, printer) -> None:
    #     board = Sudoku({}).from_model(model)
    #     print(board)


clingo.application.clingo_main(ClingoApp())
