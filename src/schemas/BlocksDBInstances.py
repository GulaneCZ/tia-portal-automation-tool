from schema import Schema, And, Or, Use, Optional, SchemaError

from src.modules.BlocksDBInstances import CallOptionEnum
from src.schemas.ProgramBlocks import Database


SingleInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": And(str, Use(CallOptionEnum)),
})

MultiInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": And(str, Use(CallOptionEnum)),
})

ParameterInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": And(str, Use(CallOptionEnum)),
})
