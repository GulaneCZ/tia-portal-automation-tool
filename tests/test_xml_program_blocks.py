from pathlib import Path
import json
import xml.etree.ElementTree as ET

from src.core.core import helper_clean_variable_sections, helper_clean_network_sources
from src.modules.XML.ProgramBlocks import PlcEnum, LibraryData
from src.schemas import configuration
import src.modules.BlocksData as BlocksData
import src.modules.BlocksFB as BlocksFB
import src.modules.BlocksOB as BlocksOB

BASE_DIR = Path(__file__).parent
smc = BASE_DIR / "configs" / "smc.json"


CONFIG = None
with open(smc) as file:
    CONFIG = configuration.validate(json.load(file))


def test_organization_block():
    for ob in CONFIG.get('Program blocks'):
        if ob.get('type') != PlcEnum.OrganizationBlock:
            continue

        variable_sections = helper_clean_variable_sections(
            CONFIG.get('Variable sections'), ob.get('id'))
        network_sources = helper_clean_network_sources(
            CONFIG.get('Network sources'),
            CONFIG.get('Program blocks'),
            CONFIG.get('Variable sections'),
            ob.get('id')
        )
        data = BlocksOB.OrganizationBlock(
            Name=ob.get('name'),
            DeviceID=ob.get('DeviceID'),
            PlcType=ob.get('type'),
            BlockGroupPath=ob.get('blockgroup_folder'),
            Number=ob.get('number'),
            ProgrammingLanguage=ob.get('programming_language'),
            EventClass=BlocksOB.EventClassEnum.ProgramCycle,
            NetworkSources=network_sources,
            Variables=variable_sections,
            IsInstance=ob.get('is_instance'),
            LibraryData=LibraryData(
                Name=(ob.get('library_source') or {}).get('name'),
                MasterCopyFolderPath=(ob.get('library_source') or {}
                                      ).get('mastercopyfolder_path')
            ),
        )
        xml = BlocksOB.XML(data).xml()
        root = ET.fromstring(xml)

        assert root.tag == "Document"
        obxml = root.find('SW.Blocks.OB')
        assert obxml is not None
        assert obxml.attrib.get('ID') == "0"

        attr_list = obxml.find('AttributeList')
        assert attr_list is not None

        name = attr_list.find('Name')
        assert name is not None
        assert name.text == ob.get('name')

        number = attr_list.find('Number')
        assert number is not None
        assert number.text == str(
            max(123, min(ob.get('number'), 32767))
            if ob.get('number') != 1 else 1
        )

        interface = attr_list.find('Interface')
        assert interface is not None

        sections = interface.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Sections')
        assert sections is not None

        # Variable Sections
        section = sections.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Section')
        if section is None:
            continue
        assert section is not None
        # assert section.attrib.get('Name') == "Static"

        members = section.findall(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Member')


def test_function_block():
    for fb in CONFIG.get('Program blocks'):
        if fb.get('type') != PlcEnum.FunctionBlock:
            continue

        variable_sections = helper_clean_variable_sections(
            CONFIG.get('Variable sections'), fb.get('id'))
        network_sources = helper_clean_network_sources(
            CONFIG.get('Network sources'),
            CONFIG.get('Program blocks'),
            CONFIG.get('Variable sections'),
            fb.get('id')
        )
        data = BlocksFB.FunctionBlock(
            Name=fb.get('name'),
            DeviceID=fb.get('DeviceID'),
            PlcType=fb.get('type'),
            BlockGroupPath=fb.get(
                'blockgroup_folder'),
            Number=fb.get('number'),
            ProgrammingLanguage=fb.get('programming_language'),
            NetworkSources=network_sources,
            Variables=variable_sections,
            IsInstance=fb.get('is_instance'),
            LibraryData=LibraryData(
                Name=(fb.get('library_source') or {}).get('name'),
                MasterCopyFolderPath=(fb.get('library_source') or {}
                                      ).get('mastercopyfolder_path')
            ),
        )
        xml = BlocksFB.XML(data).xml()
        root = ET.fromstring(xml)

        assert root.tag == "Document"
        fbxml = root.find('SW.Blocks.FB')
        assert fbxml is not None
        assert fbxml.attrib.get('ID') == "0"
        #
        attr_list = fbxml.find('AttributeList')
        assert attr_list is not None

        name = attr_list.find('Name')
        assert name is not None
        assert name.text == fb.get('name')

        number = attr_list.find('Number')
        assert number is not None
        assert number.text == str(fb.get('number'))

        interface = attr_list.find('Interface')
        assert interface is not None

        sections = interface.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Sections')
        assert sections is not None

        # Variable Sections
        section = sections.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Section')
        if section is None:
            continue
        assert section is not None
        # assert section.attrib.get('Name') == "Static"

        members = section.findall(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Member')


def test_globaldb():
    for db in CONFIG.get('Program blocks'):
        if db.get('type') != PlcEnum.GlobalDB.value:
            continue

        variable_sections = helper_clean_variable_sections(
            CONFIG.get('Variable sections'), db.get('id'))
        data = BlocksData.DataBlock(
            DeviceID=db.get('DeviceID'),
            Name=db.get('name'),
            Number=db.get('number'),
            BlockGroupPath=db.get('blockgroup_folder', '/'),
            VariableSections=variable_sections,
            Attributes=db.get('attributes', {})
        )

        root = ET.fromstring(BlocksData.XML(data).xml())

        assert root.tag == "Document"
        gdb = root.find('SW.Blocks.GlobalDB')
        assert gdb is not None
        assert gdb.attrib.get('ID') == "0"

        attr_list = gdb.find('AttributeList')
        assert attr_list is not None

        name = attr_list.find('Name')
        assert name is not None
        assert name.text == db.get('name')

        number = attr_list.find('Number')
        assert number is not None
        assert number.text == str(db.get('number'))

        interface = attr_list.find('Interface')
        assert interface is not None

        sections = interface.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Sections')
        assert sections is not None

        # Variable Sections
        section = sections.find(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Section')
        if section is None:
            continue
        assert section is not None
        assert section.attrib.get('Name') == "Static"

        members = section.findall(
            '{http://www.siemens.com/automation/Openness/SW/Interface/v5}Member')
        # for member in members:
        #     print(member)
        #     assert member is not None
        # assert member.attrib.get('Name') == "Event_Pool"
        # assert member.attrib.get(
        #     'Datatype') == 'Array[0..999] of "Event_Pool"'
        # assert member.attrib.get('Remanence') == "Retain"
        # assert member.attrib.get('Accessibility') == "Public"
