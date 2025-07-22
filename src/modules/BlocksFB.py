from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
import logging

from src.core import logs

from src.modules.PlcBlocks import generate
from src.modules.XML.ProgramBlocks import Base, PlcEnum, LibraryData, ProgramBlock, BlockCompileUnit, VariableStruct, generate_boolean_attributes

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class FunctionBlock(ProgramBlock):
    DeviceID: int
    BlockGroupPath: PurePosixPath
    NetworkSources: list[NetworkSource]
    IsInstance: bool
    LibraryData: LibraryData


class XML(Base):
    DOCUMENT = PlcEnum.FunctionBlock.value

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
            CompileUnit = BlockCompileUnit(
                data.ProgrammingLanguage, network_source, id).root
            self.ObjectList.append(CompileUnit)
            id += 5

        return

    def _create_member(self, structs: list[VariableStruct], section: ET.Element):
        for struct in structs:
            Member = ET.SubElement(
                section,
                "Member",
                attrib={
                    'Name': struct.Name,
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


def create(TIA: Siemens.Engineering.TiaPortal,
           imports: Imports,
           plc_software: Siemens.Engineering.HW.Software,
           data: DataBlock
           ):
    logger.info(f"Generation of Function Block {data.Name} started")

    if not data.Name:
        return

    xml = XML(data)
    generate(imports=imports,
             TIA=TIA,
             plc_software=plc_software,
             data=data,
             xml=xml)
