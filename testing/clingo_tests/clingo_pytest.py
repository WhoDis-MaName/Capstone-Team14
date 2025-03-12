import subprocess
import pytest


def run_clingo(program_files):
    """Runs Clingo on the given ASP program file and returns the parsed output."""
    cmd = ["clingo"] + program_files
    # print(f"CMD: {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    # print(f"RESULT: {result}")
    return result.stdout  # Adjust parsing as needed


def parse_answer_set(output):
    """Parses Clingo output to extract the answer set."""
    # Customize this function based on Clingo's output format
    lines = output.splitlines()
    answer_sets = [
        line for line in lines if not line.startswith(("clingo", "Solving", "Answer"))
    ]

    """Filters Clingo's answer set to extract only the relevant response."""
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
            ["../../classes.lp", "../../identifyconflict.lp"],
            {"conflict_count(2377)"},
        ),
    ],
)
def test_clingo_output(input_files, expected_output):
    output = run_clingo(input_files)
    print(f"OUTPUT: {output}")
    answer_set = set(parse_answer_set(output))
    print(f"ANSWER_SET: {answer_set}")
    print(f"EXPECTED OUTPUT: {expected_output}")
    assert answer_set == expected_output, f"Unexpected output: {answer_set}"


# print(run_clingo(["classes.lp", "identifyconflict.lp"]))
