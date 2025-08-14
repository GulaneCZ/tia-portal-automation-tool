from __future__ import annotations

from pathlib import Path
from typing import Any
import base64

from src.resources import dlls
import src.modules.BlocksData as BlocksData
import src.modules.BlocksDBInstances as BlocksDBInstances
import src.modules.BlocksFB as BlocksFB
import src.modules.BlocksFC as BlocksFC
import src.modules.BlocksOB as BlocksOB
import src.modules.DeviceItems as DeviceItems
import src.modules.Devices as Devices
import src.modules.Libraries as Libraries
import src.modules.Networks as Networks
import src.modules.PlcDataTypes as PlcDataTypes
import src.modules.PlcTags as PlcTags
import src.modules.Portals as Portals
import src.modules.Projects as Projects
import src.modules.XML.ProgramBlocks as ProgramBlocks


def generate_dlls(use_contract: bool = False) -> dict[str, Path]:
    dll_paths: dict[str, Path] = {}
    for key in dlls.b64_dlls:
        if key == "Siemens.Engineering.Contract":
            if not use_contract:
                continue
            # This key has no .Hmi pair
            data = base64.b64decode(dlls.b64_dlls[key])
            dlls_dir = Path("./DLLs")
            dlls_dir.mkdir(exist_ok=True)

            save_path = dlls_dir / key
            save_path.mkdir(exist_ok=True)
            version_dll_path = save_path / "Siemens.Engineering.dll"
            with version_dll_path.open('wb') as version_dll_file:
                version_dll_file.write(data)

            dll_paths[key] = version_dll_path.absolute()
            continue

        if "Hmi" in key:
            continue

        data = base64.b64decode(dlls.b64_dlls[key])
        hmi_key = f"{key}.Hmi"
        if hmi_key not in dlls.b64_dlls:
            continue  # Skip if the HMI pair is missing

        hmi_data = base64.b64decode(dlls.b64_dlls[hmi_key])
        dlls_dir = Path("./DLLs")
        dlls_dir.mkdir(exist_ok=True)

        save_path = dlls_dir / key
        save_path.mkdir(exist_ok=True)

        version_dll_path = save_path / "Siemens.Engineering.dll"
        with version_dll_path.open('wb') as version_dll_file:
            version_dll_file.write(data)

        version_hmi_dll_path = save_path / "Siemens.Engineering.Hmi.dll"
        with version_hmi_dll_path.open('wb') as version_hmi_dll_file:
            version_hmi_dll_file.write(hmi_data)

        dll_paths[key] = version_dll_path.absolute()

    return dll_paths


def execute(imports: api.Imports, config: dict[str, Any], settings: dict[str, Any]) -> Siemens.Engineering.TiaPortal:

    devices_data = [Devices.Device(
        dev.get('p_typeIdentifier', 'PLC_1'),
        dev.get('p_name', 'NewPLCDevice'),
        dev.get('p_deviceName', ''),
        dev.get('id', 1),
        dev.get('slots_required', 2),
        Networks.NetworkInterface(
            Address=dev.get(
                'network_interface', {}).get('Address'),
            RouterAddress=dev.get(
                'network_interface', {}).get('RouterAddress'),
            UseRouter=dev.get(
                'network_interface', {}).get('UseRouter'),
            subnet_name=dev.get(
                'network_interface', {}).get('subnet_name'),
            io_controller=dev.get(
                'network_interface', {}).get('io_controller'),
        )
    )
        for dev in config.get('devices', [])
    ]
    local_modules_data = [DeviceItems.DeviceItem(
        DeviceID=module.get("DeviceID", 1),
        name=module.get("name", "Server module_1"),
        typeIdentifier=module.get(
            "typeIdentifier", "OrderNumber:6ES7 193-6PA00-0AA0/V1.1"),
        positionNumber=module.get("positionNumber", 2),
    )
        for module in config.get('Local modules', [])
    ]
    plc_tags_data = [PlcTags.PlcTagTable(
        DeviceID=table.get("DeviceID", 1),
        Name=table.get("Name", "Default tag table"),
        Tags=[PlcTags.PlcTag(
            Name=tag.get('Name'),
            DataTypeName=tag.get('DataTypeName'),
            LogicalAddress=tag.get('LogicalAddress')
        )
            for tag in table.get('Tags')
        ],
    )
        for table in config.get('PLC tags', [])
    ]
    libraries_data = [Libraries.GlobalLibrary(
        FilePath=library.get('path'),
        ReadOnly=library.get('read_only'),
    )
        for library in config.get('libraries', [])
    ]
    plc_data_types_data = [PlcDataTypes.PlcDataType(
        Name=datatype.get("Name"),
        Types=[PlcDataTypes.PlcStruct(
            Name=struct.get('Name'),
            Datatype=struct.get('Datatype'),
            attributes=struct.get('attributes'),
        )
            for struct in datatype.get('types', [])
        ],
    )
        for datatype in config.get('PLC data types', [])
    ]
    data_blocks = [BlocksData.DataBlock(
        DeviceID=db.get('DeviceID'),
        Name=db.get('name'),
        Number=db.get('number'),
        BlockGroupPath=db.get('blockgroup_folder', '/'),
        VariableSections=helper_clean_variable_sections(
            config.get('Variable sections'), db.get('id')),
        Attributes=db.get('attributes', {}))
        for db in config.get('Program blocks', [])
        if db.get('type') == ProgramBlocks.PlcEnum.GlobalDB.value
    ]
    data_plcblocks = [BlocksOB.OrganizationBlock(
        DeviceID=plc.get('DeviceID'),
        PlcType=plc.get('type'),
        Name=plc.get('name'),
        Number=plc.get('number'),
        ProgrammingLanguage=plc.get('programming_language'),
        BlockGroupPath=plc.get('blockgroup_folder'),
        EventClass=BlocksOB.EventClassEnum.ProgramCycle,
        Parameters=helper_clean_wires(
            plc.get('name'),
            plc.get('id'),
            config.get('Wire parameters'),
            config.get('Wire template')
        ),
        NetworkSources=helper_clean_network_sources(
            config.get('Network sources'),
            config.get('Program blocks'),
            config.get('Variable sections'),
            plc.get('id'),
            config.get('Wire template'),
            config.get('Wire parameters'),
            config.get('Instances'),
        ),
        Variables=helper_clean_variable_sections(
            config.get('Variable sections'), plc.get('id')),
        IsInstance=plc.get('is_instance'),
        LibraryData=ProgramBlocks.LibraryData(
            Name=(plc.get('library_source') or {}).get('name'),
            MasterCopyFolderPath=(plc.get('library_source') or {}
                                  ).get('mastercopyfolder_path')
        ),
    )
        for plc in config.get('Program blocks', [])
        if plc.get('type') == ProgramBlocks.PlcEnum.OrganizationBlock
    ]

    data_plcblocks += [BlocksFC.Function(
        DeviceID=plc.get('DeviceID'),
        PlcType=plc.get('type'),
        Name=plc.get('name'),
        Number=plc.get('number'),
        ProgrammingLanguage=plc.get('programming_language'),
        Parameters=helper_clean_wires(
            plc.get('name'),
            plc.get('id'),
            config.get('Wire parameters'),
            config.get('Wire template')
        ),
        BlockGroupPath=plc.get('blockgroup_folder'),
        Variables=helper_clean_variable_sections(
            config.get('Variable sections'), plc.get('id')),
        IsInstance=plc.get('is_instance'),
        LibraryData=ProgramBlocks.LibraryData(
            Name=(plc.get('library_source') or {}).get('name'),
            MasterCopyFolderPath=(plc.get('library_source') or {}
                                  ).get('mastercopyfolder_path')
        ),
    )
        for plc in config.get('Program blocks', [])
        if plc.get('type') == ProgramBlocks.PlcEnum.Function
    ]

    data_plcblocks += [BlocksFB.FunctionBlock(
        DeviceID=plc.get('DeviceID'),
        PlcType=plc.get('type'),
        Name=plc.get('name'),
        Number=plc.get('number'),
        ProgrammingLanguage=plc.get('programming_language'),
        BlockGroupPath=plc.get('blockgroup_folder'),
        Parameters=helper_clean_wires(
            plc.get('name'),
            plc.get('id'),
            config.get('Wire parameters'),
            config.get('Wire template')
        ),
        NetworkSources=helper_clean_network_sources(
            config.get('Network sources'),
            config.get('Program blocks'),
            config.get('Variable sections'),
            plc.get('id'),
            config.get('Wire template'),
            config.get('Wire parameters'),
            config.get('Instances'),
        ),
        Variables=helper_clean_variable_sections(
            config.get('Variable sections'), plc.get('id')),
        Database=helper_clean_database_instance(
            plc.get('id'), config.get('Instances')),
        IsInstance=plc.get('is_instance'),
        LibraryData=ProgramBlocks.LibraryData(
            Name=(plc.get('library_source') or {}).get('name'),
            MasterCopyFolderPath=(plc.get('library_source') or {}
                                  ).get('mastercopyfolder_path')
        ),
    )
        for plc in config.get('Program blocks', [])
        if plc.get('type') == ProgramBlocks.PlcEnum.FunctionBlock
    ]

    SE: Siemens.Engineering = imports.DLL
    TIA: Siemens.Engineering.TiaPortal = Portals.connect(
        imports, config, settings)

    project_data = Projects.Project(
        config['name'], config['directory'], config['overwrite'])
    se_project: Siemens.Engineering.Project = Projects.create(
        imports, project_data, TIA)

    for library in libraries_data:
        Libraries.import_library(imports, library, TIA)
    se_devices: list[Siemens.Engineering.HW.Device] = Devices.create(
        devices_data, se_project)
    se_interfaces: list[Siemens.Engineering.HW.Features.NetworkInterface] = []
    for i in range(len(devices_data)):
        se_device: Siemens.Engineering.HW.Device = se_devices[i]
        device_data: Devices.Device = devices_data[i]

        # Devices:
        se_plc_software: Siemens.Engineering.HW.Software = Devices.get_plc_software(
            imports, se_device)

        # Add Mastercopies from Libraries
        for library in libraries_data:
            name = library.FilePath.stem
            Libraries.generate_mastercopies(name, se_plc_software, TIA)

        # Networks:
        se_net_itfs: list[Siemens.Engineering.HW.Features.NetworkInterface] = Networks.create_network_service(
            imports, device_data, se_device)
        network: Networks.NetworkInterface = device_data.NetworkInterface
        for index, se_net_itf in enumerate(se_net_itfs):
            # WARNING:
            # Subnet Name must be UNIQUE!
            # Otherwise, Siemens Engineering will cause an error.
            if index == 0:
                subnet: Siemens.Engineering.HW.Subnet = se_net_itf.Nodes[0].CreateAndConnectToSubnet(
                    network.subnet_name)
                io_system: Siemens.Engineering.HW.IoSystem = se_net_itf.IoControllers[0].CreateIoSystem(
                    network.io_controller)
            else:
                se_net_itf.Nodes[0].ConnectToSubnet(subnet)
                if se_net_itf.IoConnectors.Count > 0:
                    se_net_itf.IoConnectors[0].ConnectToIoSystem(io_system)

        # DeviceItems:
        for local_module in local_modules_data:
            if local_module.DeviceID != device_data.ID:
                continue
            DeviceItems.plug_new(local_module, se_device,
                                 device_data.SlotsRequired)

        # PLC Tags:
        for plc_tag_table in plc_tags_data:
            if plc_tag_table.DeviceID != device_data.ID:
                continue
            PlcTags.new(plc_tag_table, se_plc_software)

        # PLC Data Types:
        for plc_data_type in plc_data_types_data:
            PlcDataTypes.create(imports, se_plc_software, plc_data_type)

        # Data Blocks
        for data_block in data_blocks:
            if data_block.DeviceID != device_data.ID:
                continue
            BlocksData.create(imports, se_plc_software, data_block)

        # ProgramBlocks
        for plc in data_plcblocks:
            if plc.DeviceID != device_data.ID:
                continue
            match plc.PlcType:
                case ProgramBlocks.PlcEnum.OrganizationBlock:
                    BlocksOB.create(
                        imports=imports,
                        TIA=TIA,
                        plc_software=se_plc_software,
                        data=plc)
                case ProgramBlocks.PlcEnum.FunctionBlock:
                    BlocksFB.create(
                        imports=imports,
                        TIA=TIA,
                        plc_software=se_plc_software,
                        data=plc)
                case ProgramBlocks.PlcEnum.Function:
                    BlocksFC.create(
                        imports=imports,
                        TIA=TIA,
                        plc_software=se_plc_software,
                        data=plc)

    return TIA


def helper_clean_variable_sections(variable_sections: list[dict],
                                   plc_block_id: int) -> list[ProgramBlocks.VariableSection]:
    sections: list[ProgramBlocks.VariableSection] = []

    for section in variable_sections:
        if section.get('plc_block_id') != plc_block_id:
            continue
        name = section.get('name')
        structs: list[ProgramBlocks.VariableStruct] = []
        for struct in section.get('data'):
            structs.append(ProgramBlocks.VariableStruct(
                Name=struct.get('name'),
                Datatype=struct.get('datatype'),
                Retain=struct.get('retain'),
                StartValue=struct.get('start_value'),
                Attributes=struct.get('attributes'),
            ))
        sections.append(ProgramBlocks.VariableSection(
            Name=name, Structs=structs))

    return sections


def helper_clean_network_sources(network_sources: list[dict],
                                 plcblocks: list[dict],
                                 variable_sections: list[dict],
                                 plc_block_id: int,
                                 wire_template: list[dict],
                                 wire_parameters: list[dict],
                                 instances: list[dict]) -> list[ProgramBlocks.NetworkSource]:
    networks: list[ProgramBlocks.NetworkSource] = []

    for network in network_sources:
        if network.get('plc_block_id') != plc_block_id:
            continue
        title = network.get('title')
        comment = network.get('comment')
        c_plcblocks: list[ProgramBlocks.ProgramBlock] = []

        for block in plcblocks:
            if block.get('network_source_id') != network.get('id'):
                continue

            # Organization Block
            if block.get('type') == ProgramBlocks.PlcEnum.OrganizationBlock:
                c_plcblocks.append(
                    BlocksOB.OrganizationBlock(
                        DeviceID=block.get('DeviceID'),
                        PlcType=block.get('type'),
                        Name=block.get('name'),
                        Number=block.get('number'),
                        ProgrammingLanguage=block.get(
                            'programming_language'),
                        BlockGroupPath=block.get('blockgroup_folder'),
                        Variables=helper_clean_variable_sections(
                            variable_sections, block.get('id')),
                        NetworkSources=helper_clean_network_sources(
                            network_sources,
                            plcblocks,
                            variable_sections,
                            block.get('id')),
                        EventClass=BlocksOB.EventClassEnum.ProgramCycle,
                        IsInstance=block.get('is_instance'),
                        LibraryData=ProgramBlocks.LibraryData(
                            Name=(block.get('library_source')
                                  or {}).get('name'),
                            MasterCopyFolderPath=(block.get('library_source') or {}
                                                  ).get('mastercopyfolder_path'))
                    )
                )

            # Function Block
            if block.get('type') == ProgramBlocks.PlcEnum.FunctionBlock:
                c_plcblocks.append(
                    BlocksFB.FunctionBlock(
                        DeviceID=block.get('DeviceID'),
                        PlcType=block.get('type'),
                        Name=block.get('name'),
                        Number=block.get('number'),
                        ProgrammingLanguage=block.get(
                            'programming_language'),
                        BlockGroupPath=block.get('blockgroup_folder'),
                        Variables=helper_clean_variable_sections(
                            variable_sections, block.get('id')),
                        NetworkSources=helper_clean_network_sources(
                            network_sources,
                            plcblocks,
                            variable_sections,
                            block.get('id'),
                            wire_template,
                            wire_parameters,
                            instances),
                        Parameters=helper_clean_wires(
                            block.get('name'),
                            block.get('id'),
                            wire_template,
                            wire_parameters),
                        Database=helper_clean_database_instance(
                            block.get('id'), instances),
                        IsInstance=block.get('is_instance'),
                        LibraryData=ProgramBlocks.LibraryData(
                            Name=(block.get('library_source')
                                  or {}).get('name'),
                            MasterCopyFolderPath=(block.get('library_source')
                                                  or {}).get(
                                'mastercopyfolder_path'))
                    )

                )

            # Functions
            if block.get('type') == ProgramBlocks.PlcEnum.Function:
                c_plcblocks.append(
                    BlocksFC.Function(
                        PlcType=block.get('type'),
                        Name=block.get('name'),
                        Number=block.get('number'),
                        ProgrammingLanguage=block.get(
                            'programming_language'),
                        Variables=helper_clean_variable_sections(
                            variable_sections, block.get('id')),
                        DeviceID=block.get('DeviceID'),
                        BlockGroupPath=block.get('blockgroup_folder'),
                        Parameters=helper_clean_wires(
                            block.get('name'),
                            block.get('id'),
                            wire_parameters,
                            wire_template
                        ),
                        IsInstance=block.get('is_instance'),
                        LibraryData=ProgramBlocks.LibraryData(
                            Name=(block.get('library_source')
                                  or {}).get('name'),
                            MasterCopyFolderPath=(block.get('library_source')
                                                  or {}).get(
                                'mastercopyfolder_path'))
                    )
                )

        networks.append(ProgramBlocks.NetworkSource(Title=title,
                                                    Comment=comment,
                                                    PlcBlocks=c_plcblocks,
                                                    )
                        )

    return networks


def helper_clean_wires(block_name: str,
                       plc_block_id: int,
                       wire_parameters: list[dict],
                       template: list[dict]
                       ) -> list[ProgramBlocks.WireParameter]:
    wires: list[ProgramBlocks.WireParameter] = []

    wire_parameters_template: list[dict[str, str]] = []
    parameters: dict[str, str] = {}
    for wire_block in template:
        if wire_block.get('block_name') == block_name:
            wire_parameters_template = wire_block.get('parameters')
            break

    for wire in wire_parameters:
        if wire.get('plc_block_id') == plc_block_id:
            parameters = wire.get('parameters')

    if 'en' in parameters:
        en = ProgramBlocks.WireParameter(
            Name="en",
            Section="",
            Datatype="Bool",
            Value=wire.get("en", ''),
            Negated=False
        )
        wires.append(en)

    for param in wire_parameters_template:
        wire = ProgramBlocks.WireParameter(
            Name=param.get('name'),
            Section=param.get('section'),
            Datatype=param.get('datatype'),
            Value=parameters.get(param.get('name')),
            Negated=param.get('negated')
        )
        wires.append(wire)

    return wires


def helper_clean_database_instance(plc_block_id: int,
                                   instances: list[dict]
                                   ) -> list[BlocksDBInstances.Instance]:

    for instancedb in instances:
        if instancedb.get('plc_block_id') == plc_block_id:
            return BlocksDBInstances.Instance(
                CallOption=instancedb.get('call_option'),
                Name=instancedb.get('name'),
                Number=instancedb.get('number'),
                BlockGroupPath=instancedb.get('blockgroup_folder')
            )
