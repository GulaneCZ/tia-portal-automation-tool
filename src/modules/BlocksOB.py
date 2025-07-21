from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import logging

from src.core import logs
from src.modules.PlcBlocks import import_xml_to_block_group
from src.modules.XML.ProgramBlocks import Base, PlcEnum, ProgramBlock, NetworkSource, BlockCompileUnit

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


class EventClassEnum(Enum):
    ProgramCycle = "ProgramCycle"
    Startup = "Startup"


@dataclass
class OrganizationBlock(ProgramBlock):
    DeviceID: int
    BlockGroupPath: PurePosixPath
    NetworkSources: list[NetworkSource]
    EventClass: EventClassEnum


class XML(Base):
    DOCUMENT = PlcEnum.OrganizationBlock.value

    def __init__(self, data: OrganizationBlock) -> None:
        # EventClasses have different number rules
        data.Number = max(123, min(data.Number, 32767)
                          ) if data.Number != 1 else 1
        super().__init__(data.Name, data.Number, data.ProgrammingLanguage, data.Variables)

        # default is ProgramCycle
        ET.SubElement(self.AttributeList,
                      "SecondaryType").text = data.EventClass.value
        self._create_input_section()
        self._create_temp_section()
        self._create_constant_section()
        ET.SubElement(self.InputSection, "Member", attrib={
            "Name": "Initial_Call",
            "Datatype": "Bool",
            "Informative": "true",
        })
        ET.SubElement(self.InputSection, "Member", attrib={
            "Name": "Remanence",
            "Datatype": "Bool",
            "Informative": "true",
        })

        block_id = 3
        for network_source in data.NetworkSources:
            CompileUnit = BlockCompileUnit(
                data.ProgrammingLanguage, network_source, block_id).root
            self.ObjectList.append(CompileUnit)
            block_id += 5


def create(imports: Imports, plc_software: Siemens.Engineering.HW.Software, data: DataBlock):
    logger.info(f"Generation of Organization Block {data.Name} started")

    if not data.Name:
        return

    xml = XML(data)
    filename: Path = xml.write()

    logger.info(f"Written Organization Block {data.Name} XML to: {filename}")

    import_xml_to_block_group(imports, plc_software, xml_location=filename,
                              blockgroup_folder=data.BlockGroupPath,
                              mkdir=True)
    if filename.exists():
        filename.unlink()
