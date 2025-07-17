from schema import Schema

from src.modules.BlocksDBInstances import CallOptionEnum
from src.schemas.ProgramBlocks import Database


SingleInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": CallOptionEnum.Single.value
})

MultiInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": CallOptionEnum.Multi.value
})

ParameterInstance = Schema({
    **Database._schema,
    "plc_block_id": int,
    "call_option": CallOptionEnum.Parameter.value
})
