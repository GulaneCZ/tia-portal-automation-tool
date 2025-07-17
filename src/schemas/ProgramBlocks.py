from schema import Schema, And, Or, Use, Optional, SchemaError

from src.modules.XML.ProgramBlocks import PlcEnum

VariableStruct = Schema({
    "name": str,
    "datatype": str,
    Optional("retain", default=True): bool,
    Optional("start_value", default=""): str,
    Optional("attributes", default={}): dict,
})

VariableSection = Schema({
    "plc_block_id": int,
    "name": str,
    "data": And(list, [VariableStruct]),
})

PlcBlock = Schema({
    "DeviceID": int,
    "id": int,
    Optional("network_source_id"): int,
    "type": And(str, Use(PlcEnum)),
    "name": str,
    Optional("blockgroup_folder", default="/"): str,
    Optional("number", default=1): int,
    Optional("is_instance", default=False): bool,
    Optional("library_source"): Schema({
        "name": str,
        "blockgroup_folder": str,
    }),
})

Parameter = Schema({
    "plc_block_id": int,
    "parameters": dict,
})

Database = Schema({
    "id": int,
    "name": str,
    Optional("blockgroup_folder", default="/"): str,
    Optional("number", default=1): int,
})
