from django.http import JsonResponse
import os
import clingo
from ..models import FilteredUpload
from django.core.files.storage import default_storage


def run_clingo_identifier(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not default_storage.exists(asp_filename):
            return JsonResponse(
                {"error": f"ASP file '{asp_filename}' not found."}, status=404
            )

        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_file_path = os.path.join(root_dir, "media", asp_filename)
        clingo_dir = os.path.join(root_dir, "clingo")
        overlap_path = os.path.join(clingo_dir, "overlap_identifier.lp")

        ctl = clingo.Control()
        ctl.load(asp_file_path)
        ctl.load(overlap_path)
        ctl.ground()

        result = []

        def on_model(model):
            # Only collect shown atoms
            atoms = [str(s) for s in model.symbols(shown=True)]
            result.extend(atoms)

        ctl.solve(on_model=on_model)

        return JsonResponse(
            {
                "status": "success",
                "message": f"Clingo solver executed on {asp_filename}.",
                "models": result or ["No solution found."],
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
