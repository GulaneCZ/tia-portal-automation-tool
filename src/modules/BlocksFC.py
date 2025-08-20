from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
import logging

from src.core import logs

from src.modules.ProgramBlocks import generate
from src.modules.ProgramBlocks import Base, ProgramBlock, WireParameter

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class Function(ProgramBlock):
    DeviceID: int
    BlockGroupPath: PurePosixPath
    IsInstance: bool
    LibraryData: LibraryData
    Parameters: list[WireParameter]


class XML(Base):
    DOCUMENT = "SW.Blocks.FC"

    def __init__(self, data: ProgramBlock) -> None:
        super().__init__(data.Name, data.Number, data.ProgrammingLanguage, data.Variables)

        self._create_input_section()
        self._create_output_section()
        self._create_inout_section()
        self._create_temp_section()
        self._create_constant_section()
        self._create_return_section()


def create(TIA: Siemens.Engineering.TiaPortal,
           imports: Imports,
           plc_software: Siemens.Engineering.HW.Software,
           data: Function
           ):
    logger.info(f"Generation of Function {data.Name} started")

    if not data.Name:
        return

    xml = XML(data)
    generate(imports=imports,
             TIA=TIA,
             plc_software=plc_software,
             data=data,
             xml=xml)
