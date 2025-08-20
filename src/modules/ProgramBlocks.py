from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Optional
import logging
import tempfile
import xml.etree.ElementTree as ET

from src.core import logs
from src.modules.XML import Document, XMLNS
import src.modules.BlocksDBInstances as BlocksDBInstances
import src.modules.Libraries as Libraries

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class VariableStruct:
    Name: str
    Datatype: str
    Retain: bool
    StartValue: str
    Attributes: dict


@dataclass
class VariableSection:
    Name: str
    Structs: list[VariableStruct]


@dataclass
class LibraryData:
    Name: str
    MasterCopyFolderPath: PurePosixPath


@dataclass
class ProgramBlock:
    PlcType: PlcEnum
    Name: str
    Number: int
    ProgrammingLanguage: str
    Variables: list[VariableSection]


@dataclass
class NetworkSource:
    Title: str
    Comment: str
    PlcBlocks: list[ProgramBlock]


@dataclass
class WireParameter:
    Name: str
    Section: str
    Datatype: str
    Value: AccessValue
    Negated: bool


@dataclass
class AccessValue:
    Root: str
    Variable: Optional[str]
    Index: Optional[int]

    def __init__(self, raw: str):
        if not raw:
            self.Root = ''
            self.Variable = None
            self.Index = None
            return
        parts = raw.split('.')

        self.Root = parts[0]
        self.Variable = None
        self.Index = None

        if len(parts) == 2:
            var_part = parts[1]
            self.Variable = var_part

            if '[' in var_part and var_part.endswith(']'):
                bracket_start = var_part.find('[')
                self.Variable = var_part[:bracket_start]
                self.Index = var_part[bracket_start + 1: -1]


class PlcEnum(Enum):
    PlcStruct = "SW.Types.PlcStruct"
    OrganizationBlock = "SW.Blocks.OB"
    FunctionBlock = "SW.Blocks.FB"
    Function = "SW.Blocks.FC"
    GlobalDB = "SW.Blocks.GlobalDB"
    # WatchTable = "SW.WatchAndForceTables.PlcWatchTable"
    # ForceTable = "SW.WatchAndForceTables.PlcForceTable"
    # WatchTableEntry = "SW.WatchAndForceTables.PlcWatchTableEntry"
    # ForceTableEntry = "SW.WatchAndForceTables.PlcForceTableEntry"


class Base(Document):
    def __init__(self, name: str, number: int, programming_language: str,
                 variables: list[VariableSection]):
        super().__init__(name)
        self.variables: list[VariableSection] = variables

        ET.SubElement(self.AttributeList, "Number").text = str(number)
        ET.SubElement(self.AttributeList,
                      "ProgrammingLanguage").text = programming_language
        self.ObjectList = ET.SubElement(self.SWDoc, "ObjectList")

        self.sections_enabled: list[str] = []

    def _create_input_section(self):
        self.InputSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Input"})
        self.sections_enabled.append("Input")

    def _create_output_section(self):
        self.OutputSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Output"})
        self.sections_enabled.append("Output")

    def _create_temp_section(self):
        self.TempSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Temp"})
        self.sections_enabled.append("Temp")

    def _create_constant_section(self):
        self.ConstantSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Constant"})
        self.sections_enabled.append("Constant")

    def _create_inout_section(self):
        self.InOutSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "InOut"})
        self.sections_enabled.append("InOut")

    def _create_static_section(self):
        self.StaticSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Static"})
        self.sections_enabled.append("Static")

    def _create_return_section(self):
        self.ReturnSection = ET.SubElement(
            self.Sections, "Section", attrib={"Name": "Return"})
        self.sections_enabled.append("Return")
        ET.SubElement(self.ReturnSection, "Member", attrib={
            'Name': "Ret_Val",
            'Datatype': "Void",
        })

    def _add_variables(self):
        for section in self.variables:
            if section.Name not in self.sections_enabled:
                continue

            if section.Name == "Input":
                self._create_member(section.Structs, self.InputSection)
            if section.Name == "Output":
                self._create_member(section.Structs, self.OutputSection)
            if section.Name == "Temp":
                self._create_member(section.Structs, self.TempSection)
            if section.Name == "Constant":
                self._create_member(section.Structs, self.ConstantSection)
            if section.Name == "InOut":
                self._create_member(section.Structs, self.InOutSection)
            if section.Name == "Return":
                self._create_member(section.Structs, self.ReturnSection)
            if section.Name == "Static":
                self._create_member(section.Structs, self.StaticSection)

        return

    def _create_member(self, structs: list[VariableStruct], section: ET.Element):
        for struct in structs:
            Member = ET.SubElement(
                section,
                "Member",
                attrib={
                    'Name': struct.Name,
                    'Datatype': struct.Datatype,
                    'Remanence': "Retain" if struct.Retain else "NonRetain",
                    'Accessibility': "Public"
                }
            )

            if struct.StartValue != '':
                ET.SubElement(Member, "StartValue").text = struct.StartValue

            bool_attribs = generate_boolean_attributes(struct)
            if len(bool_attribs):
                Member.append(bool_attribs)

        return


# might clean below

class BlockCompileUnit:
    def __init__(self, programming_language: str, network_source: NetworkSource, block_id):
        self.root: ET.Element = ET.Element("SW.Blocks.CompileUnit", attrib={
            'ID': format(block_id, 'X'),
            'CompositionName': "CompileUnits",
        })
        self.AttributeList = ET.SubElement(self.root, "AttributeList")
        self.ObjectList = ET.SubElement(self.root, "ObjectList")
        self.NetworkSource = ET.SubElement(self.AttributeList, "NetworkSource")
        ET.SubElement(self.AttributeList,
                      "ProgrammingLanguage").text = programming_language

        self._generate_texts(block_id+1, network_source.Title,
                             network_source.Comment)

        self._create_instances(network_source.PlcBlocks)

        return

    def _generate_texts(self, id: int, title: str, comment: str):
        Comment = generate_MultilingualText(id, "Comment", comment)
        Title = generate_MultilingualText(id + 2, "Title", title)
        self.ObjectList.append(Comment)
        self.ObjectList.append(Title)

        return

    def _create_instances(self, plcblocks: list):
        if not plcblocks:
            return

        self.FlgNet = ET.SubElement(self.NetworkSource, "FlgNet")
        self.FlgNet.set('xmlns', XMLNS.FLGNET.value)
        self.Parts = ET.SubElement(self.FlgNet, "Parts")
        self.Wires = ET.SubElement(self.FlgNet, "Wires")

        for plcblock in plcblocks:
            # for now, we only do 1 instance per network source
            if len(plcblocks) == 1:
                last_uid = self._insert_parts(plcblock, 21)
                self._insert_wires(plcblock, last_uid + 2)

        return

    def _insert_parts(self, plcblock: ProgramBlock, uid: int) -> int:
        for parameter in plcblock.Parameters:
            if not parameter.Value.Root:
                continue

            parameter.__dict__['UId'] = uid
            access = generate_access(parameter, uid)
            self.Parts.append(access)
            uid += 1
        for parameter in plcblock.Parameters:
            parameter.__dict__['call'] = uid

        Call = ET.SubElement(self.Parts, "Call", attrib={'UId': str(uid)})
        CallInfo = ET.SubElement(
            Call,
            "CallInfo",
            attrib={
                'Name': plcblock.Name,
                'BlockType': plcblock.PlcType.value.split('.')[-1]
            }
        )

        if plcblock.PlcType != PlcEnum.Function:
            scope = "GlobalVariable"
            if plcblock.Database.CallOption == BlocksDBInstances.CallOptionEnum.Multi:
                scope = "LocalVariable"
            InstanceTag = ET.SubElement(CallInfo, "Instance", attrib={
                                        'Scope': scope, 'UId': str(uid+1)})
            db_name = plcblock.Database.Name if plcblock.Database.Name != "" else f"{
                plcblock.Name}_DB"
            ET.SubElement(InstanceTag, "Component", attrib={'Name': db_name})

        for parameter in plcblock.Parameters:
            if parameter.Negated:
                ET.SubElement(Call, "Negated", attrib={'Name': parameter.Name})
            if parameter.Name == "en":
                continue
            ET.SubElement(CallInfo, "Parameter", attrib={
                'Name': parameter.Name,
                'Section': parameter.Section,
                'Type': parameter.Datatype
            })

        return uid

    def _insert_wires(self, instance: ProgramBlock, last_uid: int):
        wire_values: list[tuple[ET.Element, ET.Element]] = []
        for param in instance.Parameters:
            p_call_uid = param.__dict__.get('call', 23)
            NameCon = ET.Element("NameCon", attrib={
                                 'UId': str(p_call_uid), 'Name': param.Name})
            if param.Value.Root:
                ident_uid = param.__dict__.get('UId', 23)
                IdentCon = ET.Element("IdentCon", attrib={
                                      'UId': str(ident_uid)})
                wire_values.append((NameCon, IdentCon))

            else:
                OpenCon = ET.Element("OpenCon", attrib={'UId': str(last_uid)})
                wire_values.append((NameCon, OpenCon))

                last_uid += 1

        for data in wire_values:
            Wire = wrap_wire_data(data, last_uid)
            self.Wires.append(Wire)
            last_uid += 1

        return


class Access:
    def __init__(self, uid: int, scope: str) -> None:
        if uid == -1:
            self.Access = ET.Element(
                "Access", attrib={
                    "Scope": scope
                })
        else:
            self.Access = ET.Element(
                "Access", attrib={
                    "Scope": scope,
                    "UId": str(uid),
                })

        return

    def _create_symbol_constant(self, name: str):
        self.Value = ET.SubElement(self.Access, name)

        return


class AccessGlobalVariable(Access):
    def __init__(self, value: list, uid: int) -> None:
        super().__init__(uid, "GlobalVariable")

        self._create_symbol_constant("Symbol")
        ET.SubElement(self.Value, "Component", attrib={'Name': value.Root})
        

        if value.Index:
            Component = ET.SubElement(self.Value, "Component", attrib={
                'Name': value.Variable, 'AccessModifier': "Array"})
            Component.append(AccessLiteralConstant(
                value.Index, "DInt", -1).Access)
        else:
            ET.SubElement(self.Value, "Component", attrib={'Name': value.Variable})
            
        return


class AccessLiteralConstant(Access):
    def __init__(self, value: str, const_type: str, uid: int) -> None:
        super().__init__(uid, "LiteralConstant")

        self._create_symbol_constant("Constant")
        ET.SubElement(self.Value, "ConstantType").text = const_type
        ET.SubElement(self.Value, "ConstantValue").text = value

        return


class AccessTypedConstant(Access):
    def __init__(self, value: str, uid: int) -> None:
        super().__init__(uid, "TypedConstant")

        self._create_symbol_constant("Constant")
        ET.SubElement(self.Value, "ConstantValue").text = value

        return


def generate_MultilingualTextItem(id: int, text: str) -> ET.Element:
    root = ET.Element("MultilingualTextItem", attrib={
        'ID': format(id, 'X'),
        'CompositionName': "Items"
    })

    AttributeList = ET.SubElement(root, "AttributeList")
    ET.SubElement(AttributeList, "Culture").text = "en-US"
    ET.SubElement(AttributeList, "Text").text = text

    return root


def generate_MultilingualText(id: int, composition_name: str, text: str) -> ET.Element:
    root = ET.Element("MultilingualText", attrib={
        'ID': format(id, 'X'),
        'CompositionName': composition_name
    })
    MultilingualTextItem = generate_MultilingualTextItem(id+1, text)
    ObjectList = ET.SubElement(root, "ObjectList")
    ObjectList.append(MultilingualTextItem)

    return root


def wrap_wire_data(elements: tuple[ET.Element, ET.Element], uid: int) -> ET.Element:
    Wire = ET.Element("Wire", attrib={'UId': str(uid)})
    for el in elements:
        Wire.append(el)
    return Wire


def generate_boolean_attributes(struct: VariableStruct) -> ET.Element:
    AttributeList = ET.Element("AttributeList")
    for attrib in struct.Attributes:
        ET.SubElement(AttributeList, "BooleanAttribute", attrib={
            'Name': attrib,
            'SystemDefined': "true"
        }).text = str(struct.Attributes[attrib]).lower()

    return AttributeList


def generate_access(parameter: WireParameter, uid: int) -> ET.Element:
    if parameter.Value.Variable:
        Access = AccessGlobalVariable(parameter.Value, uid)
        return Access.Access

    if parameter.Datatype in ["Int", "Bool", "UInt", "DInt"]:
        Access = AccessLiteralConstant(
            parameter.Value.Root, parameter.Datatype, uid)
        return Access.Access

    Access = AccessTypedConstant(parameter.Value.Root, uid)
    return Access.Access


def export_xml(imports: Imports,
               plcblock: Siemens.Engineering.SW.Blocks.PlcBlock
               ) -> str:
    SE: Siemens.Engineering = imports.DLL
    FileInfo: FileInfo = imports.FileInfo

    logging.info(f"Started export of PlcBlock {plcblock.Name} XML")

    filename = tempfile.mktemp()
    filepath = Path(filename)
    plcblock.Export(FileInfo(filepath.absolute().as_posix()),
                    getattr(SE.ExportOptions, "None"))

    with open(filepath) as file:
        file.seek(3)  # get rid of the random weird bytes
        xml_data = file.read()

    filepath.unlink()

    logging.debug(f"Extracted XML: {xml_data}")

    return xml_data


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


def find(plc_software: Siemens.Engineering.HW.Software,
         blockgroup_folder: PurePosixPath,
         name: str
         ) -> Siemens.Engineering.SW.Blocks.PlcBlock:
    if not name:
        return

    blockgroup: Siemens.Engineering.SW.Blocks.PlcBlockGroup = locate_blockgroup(
        plc_software, blockgroup_folder)

    if not blockgroup:
        return

    plcblock: Siemens.Engineering.SW.Blocks.PlcBlock = blockgroup.Blocks.Find(
        name)

    return plcblock


def generate(imports: Imports,
             TIA: Siemens.Engineering.TiaPortal,
             plc_software: Siemens.Engineering.HW.Software,
             data: ProgramBlock,
             xml: Base
             ):

    if data.IsInstance:
        # if we want to copy from GLOBAL LIBRARY
        if not isinstance(data.LibraryData, dict):
            library_name = data.LibraryData.Name
            mastercopyfolder_path = data.LibraryData.MasterCopyFolderPath

            library = Libraries.find(TIA=TIA, name=library_name)

            logging.debug(f"Library: {library_name}")
            logging.debug(f"MasterCopyFolder Path: {mastercopyfolder_path}")

            mastercopy = Libraries.find_mastercopy(
                library=library,
                mastercopyfolder_path=mastercopyfolder_path,
                name=data.Name)

            if not mastercopy:
                logging.debug("MasterCopy is (null)")
                return

            blockgroup = locate_blockgroup(
                plc_software=plc_software,
                blockgroup_folder=data.BlockGroupPath,
                mkdir=True)

            if not blockgroup:
                return

            blockgroup.Blocks.CreateFrom(mastercopy)

    else:
        filename: Path = xml.write()

        logger.info(f"Written Program Block ({
                    data.Name}) XML data to: {filename}")
        import_xml_to_block_group(
            imports=imports,
            plc_software=plc_software,
            xml_location=filename,
            blockgroup_folder=data.BlockGroupPath,
            mkdir=True)

        if filename.exists():
            filename.unlink()
