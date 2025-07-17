from schema import Schema, And, Or, Use, Optional, SchemaError


NetworkSource = Schema({
    "plc_block_id": int,
    "id": int,
    Optional("title", default=""): str,
    Optional("comment", default=""): str,
})

Parameter = Schema({
    "plc_block_id": int,
    "parameters": {str: str},
})
