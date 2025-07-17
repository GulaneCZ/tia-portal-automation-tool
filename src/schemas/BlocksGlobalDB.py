from schema import Schema, And, Or, Use, Optional, SchemaError

from src.schemas.ProgramBlocks import Database, VariableStruct

GlobalDB = Schema({
    **Database.schema,
    "DeviceID": int,
    Optional("structs", default=[]): And(list, [VariableStruct]),
    Optional("attributes", default={}): dict,
})
