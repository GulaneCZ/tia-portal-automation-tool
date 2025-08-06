from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import logging
import xml.etree.ElementTree as ET

from src.core import logs
from src.modules.BlocksDatabase import Database
from src.modules.XML.ProgramBlocks import VariableSection
from src.modules.XML.ProgramBlocks import Base, PlcEnum
from src.modules.PlcBlocks import import_xml_to_block_group

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class DataBlock(Database):
    DeviceID: int
    VariableSections: list[VariableSection]
    Attributes: dict


class XML(Base):
    DOCUMENT = PlcEnum.GlobalDB.value

    def __init__(self, data: DataBlock):
        data.Number = max(1, min(data.Number, 599999))
        super().__init__(data.Name, data.Number, "DB", data.VariableSections)

        for section in data.VariableSections:
            match section.Name:
                case "Static":
                    self._create_static_section()
                case "Input":
                    self._create_input_section()
                case "InOut":
                    self._create_inout_section()
                case "Output":
                    self._create_output_section()

        self._add_variables()

        for attrib in data.Attributes:
            ET.SubElement(self.AttributeList,
                          attrib).text = data.Attributes[attrib]

        return


def create(imports: Imports, plc_software: Siemens.Engineering.HW.Software, data: DataBlock):
    logger.info(f"Generation of Data Block {data.Name} started")

    if not data.Name:
        return

    xml = XML(data)
    filename: Path = xml.write()

    logger.info(f"Written Data Block {data.Name} XML to: {filename}")

    import_xml_to_block_group(imports, plc_software, xml_location=filename,
                              blockgroup_folder=data.BlockGroupPath,
                              mkdir=True)
    if filename.exists():
        filename.unlink()
