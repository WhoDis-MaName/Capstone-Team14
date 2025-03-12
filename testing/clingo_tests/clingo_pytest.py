import subprocess
import pytest


def run_clingo(program_files):
    """Runs Clingo on the given ASP program file and returns the parsed output."""
    cmd = ["clingo"] + program_files
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout  # Adjust parsing as needed


def parse_answer_set(output):
    """Parses Clingo output to extract the answer set."""
    # Customize this function based on Clingo's output format
    lines = output.splitlines()
    answer_sets = [
        line for line in lines if not line.startswith(("clingo", "Solving", "Answer"))
    ]
    return answer_sets


@pytest.mark.parametrize(
    "input_files,expected_output",
    [
        (
            ["classes.lp", "identifyconflict.lp"],
            {"conflict_count(2377)"},
        ),
    ],
)
def test_clingo_output(input_files, expected_output):
    output = run_clingo(input_files)
    answer_set = set(parse_answer_set(output))
    assert answer_set == expected_output, f"Unexpected output: {answer_set}"


# print(run_clingo(["classes.lp", "identifyconflict.lp"]))
