from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
import logging

from src.core import logs
from src.modules.XML.Documents import PlcStruct, import_xml
from src.modules.XML.Softwares import Software

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class PlcDataType:
    Name: str
    Types: list[PlcStruct]


class XML(Software):
    DOCUMENT = "SW.Types.PlcStruct"
    def __init__(self, data: PlcDataType):
        super().__init__(data.Name)

        for udt in data.Types:
            self._add_member(udt.Name, udt.Datatype, udt.attributes)


    def _add_member(self, name: str, datatype: str, attributes: dict):
        Member: ET.Element = ET.SubElement(self.Section, "Member", attrib={
            "Name": name,
            "Datatype": datatype
        })

        if not attributes: return

        AttributeList = ET.SubElement(Member, "AttributeList")
        for attrib in attributes:
            ET.SubElement(AttributeList, "BooleanAttribute", attrib={
                'Name': attrib,
                'SystemDefined': "true"
            }).text = str(attributes[attrib]).lower()


def create(imports: Imports, plc_software: Siemens.Engineering.HW.Software, data: PlcDataType):
    logger.info(f"Generating of {data.Name} User Data Types started")

    if not data.Name or not data.Types:
        return

    logger.info(f"Generating of User Data Type {data.Name} started")

    xml = XML(data)
    filename: Path = xml.write()
    
    logger.info(f"Written User Data Type {data.Name} XML to: {filename}")

    import_xml(imports, plc_software, filename)

    logger.info(f"Importing User Data Type {data.Name} started")

    if filename.exists():
        filename.unlink()
