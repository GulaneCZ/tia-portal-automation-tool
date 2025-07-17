from schema import Schema, And, Or, Use, Optional, SchemaError

from src.schemas.ProgramBlocks import PlcBlock

OrganizationBlock = Schema({
    **PlcBlock._schema,
    "programming_language": str,
    # Optional("db"): Or(schema_instancedb, schema_db),
})
