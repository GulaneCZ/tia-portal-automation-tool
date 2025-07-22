from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Optional
import logging

from src.core import logs

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GlobalLibrary:
    FilePath: Path
    ReadOnly: Optional[bool] = None


def import_library(imports: Imports, data: GlobalLibrary, TIA: Siemens.Engineering.TiaPortal) -> Siemens.Engineering.Library.GlobalLibrary:
    SE: Siemens.Engineering = imports.DLL
    FileInfo: FileInfo = imports.FileInfo

    library_path: FileInfo = FileInfo(data.FilePath.as_posix())

    logger.info(f"Opening Global Library: {
                library_path} (ReadOnly: {data.ReadOnly})")

    library: Siemens.Engineering.Library.GlobalLibrary = SE.Library.GlobalLibrary
    if data.ReadOnly:
        library = TIA.GlobalLibraries.Open(library_path, SE.OpenMode.ReadOnly)
        logger.info(f"Opened Global Library in Read-Only Mode: {library.Name}")
    else:
        library = TIA.GlobalLibraries.Open(library_path, SE.OpenMode.ReadWrite)
        logger.info(
            f"Opened Global Library in Read-Write Mode: {library.Name}")

    return library


def copy_mastercopies_to_plc_group(mastercopyfolder: Siemens.Engineering.Library.MasterCopies.MasterCopyFolder, block_group: Siemens.Engineering.SW.Blocks.PlcBlockGroup):
    if not mastercopyfolder:
        return

    logger.info(f"Started cloning of Mastercopies of MasterCopyFolder {
                mastercopyfolder.Name} to PlcBlockGroup {block_group.Name}")

    for folder in mastercopyfolder.Folders:
        if folder.Name == "__":
            continue
        new_block_group = block_group.Groups.Create(folder.Name)

        logger.info(f"Copied MasterCopyFolder {folder.Name}")

        copy_mastercopies_to_plc_group(folder, new_block_group)

    for mastercopy in mastercopyfolder.MasterCopies:
        logger.info(f"Copied MasterCopy {mastercopy.Name}")

        block_group.Blocks.CreateFrom(mastercopy)

    return


def generate_mastercopies(name: str, plc_software: Siemens.Engineering.HW.Software, TIA: Siemens.Engineering.TiaPortal):
    logger.info(f"Copying of Global Library {
                name} to {plc_software.Name} started")

    library: Siemens.Engineering.Library.GlobalLibrary = find(
        TIA, name)
    if not library:
        return
    mastercopyfolder: Siemens.Engineering.Library.MasterCopies.MasterCopySystemFolder = library.MasterCopyFolder
    root_block_group: Siemens.Engineering.SW.Blocks.PlcBlockGroup = plc_software.BlockGroup.Groups.Create(
        library.Name)

    copy_mastercopies_to_plc_group(mastercopyfolder, root_block_group)

    return


def find(TIA: Siemens.Engineering.TiaPortal, name: str) -> Siemens.Engineering.Library.GlobalLibrary:
    logger.info(f"Search for Library {name} started")
    logger.debug(f"List of GlobalLibraries: {TIA.GlobalLibraries}")

    for global_library in TIA.GlobalLibraries:
        if global_library.Name == name:
            logger.info(f"Found Library {global_library.Name}")
            return global_library


def find_mastercopy(library: Siemens.Engineering.Library.GlobalLibrary,
                    mastercopyfolder_path: PurePosixPath,
                    name: str) -> Siemens.Engineering.Library.MasterCopies.MasterCopy:
    if not name:
        return
    if not library:
        return

    mastercopyfolder = locate_mastercopyfolder(
        library=library, mastercopyfolder_path=mastercopyfolder_path)

    if not mastercopyfolder:
        return

    mastercopy = mastercopyfolder.MasterCopies.Find(name)

    return mastercopy


def locate_mastercopyfolder(library: Siemens.Engineering.Library.GlobalLibrary,
                            mastercopyfolder_path: PurePosixPath) -> Siemens.Engineering.Library.MasterCopies.MasterCopyUserFolder:

    if not mastercopyfolder_path.is_absolute():
        mastercopyfolder_path = PurePosixPath('/') / mastercopyfolder_path

    mastercopyfolder: Siemens.Engineering.Library.MasterCopies.MasterCopyUserFolder = library.MasterCopyFolder
    for part in mastercopyfolder_path.parts:
        if part == '/':
            continue
        mastercopyfolder = mastercopyfolder.Folders.Find(part)
        if not mastercopyfolder:
            return

    return mastercopyfolder
