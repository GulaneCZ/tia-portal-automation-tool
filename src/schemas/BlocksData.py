from schema import Schema, Use, And, Optional

from src.modules.XML.ProgramBlocks import PlcEnum
from src.schemas.ProgramBlocks import Database

GlobalDB = Schema({
    **Database.schema,
    "DeviceID": int,
    "type": And(str, Use(PlcEnum)),
    Optional("attributes", default={}): dict,
})
