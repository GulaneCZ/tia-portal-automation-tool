from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from src.modules.XML.Documents import Document
from src.modules.XML.ProgramBlocks import Base, ProgramBlock, NetworkSource, BlockCompileUnit, VariableStruct, generate_boolean_attributes

@dataclass
class FunctionBlock(ProgramBlock):
    NetworkSources: list[NetworkSource]

class FB(Base):
    DOCUMENT = "SW.Blocks.FB"
    def __init__(self, data: FunctionBlock) -> None:
        super().__init__(data.Name, data.Number, data.ProgrammingLanguage, data.Variables)

        self._create_input_section()
        self._create_output_section()
        self._create_inout_section()
        self._create_static_section()
        self._create_temp_section()
        self._create_constant_section()

        self._add_variables()

        id = 3
        for network_source in data.NetworkSources:
            CompileUnit = BlockCompileUnit(data.ProgrammingLanguage, network_source, id).root
            self.ObjectList.append(CompileUnit)
            id += 5

        return

    def _create_member(self, structs: list[VariableStruct], section: ET.Element):
        # code duplication lol
        for struct in structs:
            Member = ET.SubElement(section,
                                   "Member",
                                   attrib={'Name': struct.Name,
                                           'Datatype': struct.Datatype,
                                           'Accessibility': "Public"
                                           }
                                   )
            if struct.StartValue != '':
                ET.SubElement(Member, "StartValue").text = struct.StartValue

            bool_attribs = generate_boolean_attributes(struct)
            if len(bool_attribs):
                Member.append(bool_attribs)

        return
