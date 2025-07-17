from schema import Schema, And, Or, Use, Optional, SchemaError

from src.schemas.ProgramBlocks import PlcBlock

Function = Schema({
    **PlcBlock.schema,
})
