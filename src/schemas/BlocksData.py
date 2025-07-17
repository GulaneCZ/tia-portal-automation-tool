from schema import Schema,  Optional

from src.schemas.ProgramBlocks import Database

GlobalDB = Schema({
    **Database.schema,
    "DeviceID": int,
    "type": "SW.Blocks.GlobalDB",
    Optional("attributes", default={}): dict,
})
