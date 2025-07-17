from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from src.modules.XML.Documents import Document
from src.modules.XML.ProgramBlocks import Base, ProgramBlock, NetworkSource, BlockCompileUnit

class EventClassEnum(Enum):
    ProgramCycle = "ProgramCycle"
    Startup = "Startup"

@dataclass
class OrganizationBlock(ProgramBlock):
    NetworkSources: list[NetworkSource]
    EventClass: EventClassEnum


class OB(Base):
    DOCUMENT = "SW.Blocks.OB"
    def __init__(self, data: OrganizationBlock) -> None:
        data.Number = max(123, min(data.Number, 32767)) if data.Number != 1 else 1 # EventClasses have different number rules
        super().__init__(data.Name, data.Number, data.ProgrammingLanguage, data.Variables)

        ET.SubElement(self.AttributeList, "SecondaryType").text = data.EventClass.value # default is ProgramCycle
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

        id = 3
        for network_source in data.NetworkSources:
            CompileUnit = BlockCompileUnit(data.ProgrammingLanguage, network_source, id).root
            self.ObjectList.append(CompileUnit)
            id += 5
