import subprocess
import pytest


# TODO: make this work:

# def run_clingo(input_files):
#     # Runs Clingo with multiple input files using the Clingo Python API.
#     ctl = clingo.Control()

#     # Load each file into the Clingo control object
#     for file in input_files:
#         ctl.load(file)

#     # Ground the program
#     ctl.ground([("base", [])])

#     # Store answer sets
#     answer_sets = []

#     # Solve and collect models
#     def on_model(model):
#         answer_sets.append(model.symbols(atoms=True))

#     ctl.solve(on_model=on_model)

#     return answer_sets  # Returns a list of answer sets as clingo.Symbol objects


def run_clingo(program_files):
    # Runs Clingo on the given ASP program file and returns the parsed output.
    cmd = ["clingo"] + program_files
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout  # Adjust parsing as needed


def parse_answer_set(output):
    # Parses Clingo output to extract the answer set.
    lines = output.splitlines()
    answer_sets = [
        line for line in lines if not line.startswith(("clingo", "Solving", "Answer"))
    ]

    # Filters Clingo's answer set to extract only the relevant response.
    return {
        line
        for line in answer_sets
        if line
        and not any(
            keyword in line
            for keyword in [
                "Models",
                "Reading",
                "Calls",
                "CPU Time",
                "SATISFIABLE",
                "Time",
            ]
        )
    }


@pytest.mark.parametrize(
    "input_files,expected_output",
    [
        (
            ["../test_cases/test_case_00.lp", "../../clingo/identifyconflict.lp"],
            {"true_conflict_count(3)"},
        ),
    ],
)
def test_clingo_output(input_files, expected_output):
    output = run_clingo(input_files)
    answer_set = set(parse_answer_set(output))
    print(output)
    assert answer_set == expected_output, f"Unexpected output: {answer_set}"
