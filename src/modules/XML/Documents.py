from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

@dataclass
class PlcStruct:
    Name: str
    Datatype: str
    attributes: dict

class XMLNS(Enum):
    INTERFACE = "http://www.siemens.com/automation/Openness/SW/Interface/v5"
    FLGNET = "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"

class Base:
    DOCUMENT = None
    def __init__(self, name: str):
        self.root = ET.fromstring("<Document />") 

        if not self.DOCUMENT: raise ValueError("Section Name not set.")

        self.SWDoc = ET.SubElement(self.root, self.DOCUMENT, attrib={'ID': str(0)})
        self.AttributeList = ET.SubElement(self.SWDoc, "AttributeList")
        ET.SubElement(self.AttributeList, "Name").text = name

    def export(self, root: ET.Element) -> str:
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    def xml(self) -> str:
        return self.export(self.root)

    def write(self) -> Path:
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp:
            filename = Path(temp.name)
            temp.write(self.xml().encode('utf-8'))

        return filename

class Document(Base):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.Interface = ET.SubElement(self.AttributeList, "Interface")
        self.Sections = ET.SubElement(self.Interface, "Sections")
        self.Sections.set('xmlns', XMLNS.INTERFACE.value)
        ET.SubElement(self.AttributeList, "Namespace")



def import_xml(imports: Imports, plc_software: Siemens.Engineering.HW.Software, xml: Path):
    SE: Siemens.Engineering = imports.DLL
    FileInfo: FileInfo = imports.FileInfo

    # logging.info(f"Importing XML {xml.absolute()}...")

    xml_path: FileInfo = FileInfo(xml.absolute().as_posix())

    types: Siemens.Engineering.SW.Types.PlcTypeComposition = plc_software.TypeGroup.Types
    types.Import(xml_path, SE.ImportOptions.Override)

    # logging.info(f"Imported XML {xml_path}")

    return
