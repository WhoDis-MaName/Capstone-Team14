import subprocess
import pytest


def run_clingo(program_file):
    """Runs Clingo on the given ASP program file and returns the parsed output."""
    result = subprocess.run(["clingo", program_file], capture_output=True, text=True)
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
    "input_file,expected_output",
    [
        ("example.lp", {"expected_predicate(1)", "expected_predicate(2)"}),
        ("another_example.lp", {"another_predicate(3)", "another_predicate(4)"}),
    ],
)
def test_clingo_output(input_file, expected_output):
    output = run_clingo(input_file)
    answer_set = set(parse_answer_set(output))
    assert answer_set == expected_output, f"Unexpected output: {answer_set}"
