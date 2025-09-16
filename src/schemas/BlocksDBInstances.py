from schema import Schema, And, Use

from src.modules.BlocksDBInstances import CallOptionEnum
from src.schemas.ProgramBlocks import Database


InstanceDB = Schema({
    **Database._schema,
    "DeviceID": int,
    "plc_block_id": int,
    "call_option": And(str, Use(CallOptionEnum))
})
