from schema import Schema, And, Or, Use, Optional, SchemaError

from src.schemas.ProgramBlocks import PlcBlock

FunctionBlock = Schema({
    **PlcBlock.schema,
    "programming_language": str,
})
