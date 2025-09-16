from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
import logging

from src.core import logs

from src.modules.BlocksDatabase import Database

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


class CallOptionEnum(Enum):
    Single = "Single"
    Multi = "Multi"
    Parameter = "Parameter"


@dataclass
class InstanceDB(Database):
    Id: int
    DeviceID: int
    InstanceOfName: str
    Name: str
    CallOption: CallOptionEnum
    Number: int
    BlockGroupPath: PurePosixPath


def create(plc_software: Siemens.Engineering.HW.Software,
           data: InstanceDB):
    if not data.InstanceOfName:
        return
    if data.CallOption != CallOptionEnum.Single:
        return

    from src.modules.ProgramBlocks import locate_blockgroup  # circular dependency lol

    logger.info(f"Generation of InstanceDB '{data.Name}' of Plc '{
                data.InstanceOfName}' started")

    db_name = data.Name if data.Name != "" else f"{data.InstanceOfName}_DB"

    blockgroup = locate_blockgroup(
        plc_software, data.BlockGroupPath, mkdir=True)
    blockgroup.Blocks.CreateInstanceDB(
        db_name, True, data.Number, data.InstanceOfName)
