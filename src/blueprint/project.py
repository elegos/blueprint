import logging
from typing import List
from blueprint.settings import SettingsManager
from blueprint.function import Function
from blueprint.module_scanner import functions_scanner


class Project:
    settings_manager: SettingsManager
    functions: List[Function]
    flows: List  # TODO

    logger = logging.getLogger('Project')

    @staticmethod
    def load(settings_manager: SettingsManager) -> 'Project':
        project_root = settings_manager.settings.get_project_root()

        if not project_root:
            return

        # TODO manage functions filter
        functions = functions_scanner(project_root)
        # TODO load existing flows
        flows = []

        return Project(settings_manager=settings_manager, functions=functions, flows=flows)

    def __init__(self, settings_manager: SettingsManager, functions: List[Function], flows=List):
        self.settings_manager = settings_manager,
        self.functions = functions
        self.flows = flows

        self.logger.debug(self.functions)
