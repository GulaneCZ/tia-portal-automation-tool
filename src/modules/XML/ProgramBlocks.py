from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Optional
import xml.etree.ElementTree as ET

from src.modules.XML.Documents import Document


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
class ProgramBlock:
    Name: str
    Number: int
    ProgrammingLanguage: str
    Variables: list[VariableSection]


@dataclass
class NetworkSource:
    Title: str
    Comment: str
    Instances: list


@dataclass
class WireParameter:
    Name: str
    Section: str
    Datatype: str
    Value: str | list[str]
    Negated: bool


class PlcEnum(Enum):
    PlcStruct = "SW.Types.PlcStruct"
    OB = "SW.Blocks.OB"
    FB = "SW.Blocks.FB"
    FC = "SW.Blocks.FC"
    GlobalDB = "SW.Blocks.GlobalDB"
    # WatchTable = "SW.WatchAndForceTables.PlcWatchTable"
    # ForceTable = "SW.WatchAndForceTables.PlcForceTable"
    # WatchTableEntry = "SW.WatchAndForceTables.PlcWatchTableEntry"
    # ForceTableEntry = "SW.WatchAndForceTables.PlcForceTableEntry"


@dataclass
class Database:
    Name: str
    Number: int
    BlockGroupPath: str


@dataclass
class InstanceContainer:
    Name: str
    Type: PlcEnum
    Database: Database
    Parameters: list[WireParameter]


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
            if not section.Name in self.sections_enabled:
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
            Member = ET.SubElement(section,
                                   "Member",
                                   attrib={'Name': struct.Name,
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


class BlockCompileUnit:
    def __init__(self, programming_language: str, network_source: NetworkSource, id) -> None:
        self.root: ET.Element = ET.Element("SW.Blocks.CompileUnit", attrib={
            'ID': format(id, 'X'),
            'CompositionName': "CompileUnits",
        })
        self.AttributeList = ET.SubElement(self.root, "AttributeList")
        self.ObjectList = ET.SubElement(self.root, "ObjectList")
        self.NetworkSource = ET.SubElement(self.AttributeList, "NetworkSource")
        ET.SubElement(self.AttributeList,
                      "ProgrammingLanguage").text = programming_language

        self._generate_texts(id+1, network_source.Title,
                             network_source.Comment)

        self._create_instances(network_source.Instances)

        return

    def _generate_texts(self, id: int, title: str, comment: str):
        Comment = generate_MultilingualText(id, "Comment", comment)
        Title = generate_MultilingualText(id + 2, "Title", title)
        self.ObjectList.append(Comment)
        self.ObjectList.append(Title)

        return

    def _create_instances(self, instances: list):
        if not instances:
            return

        self.FlgNet = ET.SubElement(self.NetworkSource, "FlgNet")
        self.FlgNet.set('xmlns', XMLNS.FLGNET.value)
        self.Parts = ET.SubElement(self.FlgNet, "Parts")
        self.Wires = ET.SubElement(self.FlgNet, "Wires")

        for instance in instances:
            # for now, we only do 1 instance per network source
            if len(instances) == 1:
                last_uid = self._insert_parts(instance, 21)
                self._insert_wires(instance, last_uid + 2)

        return

    def _insert_parts(self, instance: InstanceContainer, uid: int) -> int:
        for parameter in instance.Parameters:
            if not parameter.Value:
                continue

            parameter.__dict__['UId'] = uid
            access = generate_access(parameter, uid)
            self.Parts.append(access)
            uid += 1
        for parameter in instance.Parameters:
            parameter.__dict__['call'] = uid

        Call = ET.SubElement(self.Parts, "Call", attrib={'UId': str(uid)})
        CallInfo = ET.SubElement(Call, "CallInfo", attrib={
                                 'Name': instance.Name, 'BlockType': instance.Type.value.split('.')[-1]})
        if instance.Type != PlcEnum.FC:
            scope = "GlobalVariable"
            if instance.Database.Type == DatabaseType.MultiInstance:
                scope = "LocalVariable"
            InstanceTag = ET.SubElement(CallInfo, "Instance", attrib={
                                        'Scope': scope, 'UId': str(uid+1)})
            db_name = instance.Database.Name if instance.Database.Name != "" else f"{
                instance.Name}_DB"
            ET.SubElement(InstanceTag, "Component", attrib={'Name': db_name})

        for parameter in instance.Parameters:
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

    def _insert_wires(self, instance: InstanceContainer, last_uid: int):
        wire_values: list[tuple[ET.Element, ET.Element]] = []
        for param in instance.Parameters:
            p_call_uid = param.__dict__.get('call', 23)
            NameCon = ET.Element("NameCon", attrib={
                                 'UId': str(p_call_uid), 'Name': param.Name})
            if param.Value:
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
