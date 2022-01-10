from blueprint.models import Project
from blueprint.module_scanner import functions_scanner
from blueprint.settings import Settings


def load_project(settings: Settings) -> Project:
    project_root = settings.get_project_root()

    if not project_root:
        return

    functions = functions_scanner(project_root)
    # TODO load existing flows
    flows = []

    return Project(
        settings=settings,
        functions=functions,
        flows=flows
    )
