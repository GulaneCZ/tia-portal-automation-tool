from __future__ import annotations
import logging
from pathlib import Path, PurePosixPath

from src.core import logs

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


def import_xml_to_block_group(imports: Imports,
                              plc_software: Siemens.Engineering.HW.Software,
                              xml_location: Path,
                              blockgroup_folder: PurePosixPath,
                              mkdir: bool = False
                              ) -> Siemens.Engineering.SW.Blocks.PlcBlock:
    SE: Siemens.Engineering = imports.DLL
    FileInfo: FileInfo = imports.FileInfo

    logging.info(f"Import of XML {xml_location.absolute()} started")

    xml_dotnet_path: FileInfo = FileInfo(xml_location.absolute().as_posix())

    blockgroup = locate_blockgroup(
        plc_software, blockgroup_folder, mkdir)

    plcblock: Siemens.Engineering.SW.Blocks.PlcBlock = blockgroup.Blocks.Import(
        xml_dotnet_path, SE.ImportOptions.Override)

    logging.info(f"Finished: Import of XML {xml_dotnet_path}")

    return plcblock


def locate_blockgroup(plc_software: Siemens.Engineering.HW.Software,
                      blockgroup_folder: PurePosixPath,
                      mkdir: bool = False) -> Siemens.Engineering.SW.Blocks.BlockGroup | None:
    if not blockgroup_folder.is_absolute():
        blockgroup_folder = PurePosixPath('/') / blockgroup_folder

    current_blockgroup: Siemens.Engineering.SW.Blocks.PlcBlockGroup | None = plc_software.BlockGroup
    previous_blockgroup: Siemens.Engineering.SW.Blocks.PlcBlockGroup | None = plc_software.BlockGroup
    for part in blockgroup_folder.parts:
        if part == '/':
            continue
        current_blockgroup = current_blockgroup.Groups.Find(part)
        if not current_blockgroup:
            if mkdir:
                current_blockgroup = previous_blockgroup.Groups.Create(part)
            else:
                return
        previous_blockgroup = current_blockgroup

    return current_blockgroup
