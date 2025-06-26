from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import logging

from src.core import logs
from src.modules.Portals import Imports

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class Project:
    Name: str
    Directory: Path
    Overwrite: bool


def create(imports: Imports, data: Project, TIA: Siemens.Engineering.TiaPortal) -> Siemens.Engineering.Project:
    DirectoryInfo: DirectoryInfo = imports.DirectoryInfo

    logger.info(f"Creating project {data.Name}: {data.Directory}")

    existing_project_path: DirectoryInfo = DirectoryInfo(data.Directory.joinpath(data.Name).as_posix())

    logger.info(f"Checking for existing project: {existing_project_path}")

    if existing_project_path.Exists:

        logger.info(f"{data.Name} already exists...")

        if data.Overwrite:

            logger.info(f"Deleting project {data.Name}...")

            existing_project_path.Delete(True)

            logger.info(f"Deleted project {data.Name}")

        else:
            err = f"Failed creating project. Project already exists ({existing_project_path})"
            logging.error(err)
            raise ValueError

    logger.info("No existing project exists.")

    project_path: DirectoryInfo = DirectoryInfo(data.Directory.as_posix())

    logger.debug(f"Project Path: {project_path}")

    project_composition: Siemens.Engineering.ProjectComposition = TIA.Projects
    project: Siemens.Engineering.Project = project_composition.Create(project_path, data.Name)

    logger.info(f"Created project {data.Name} at {data.Directory}")

    return project


