from schema import Schema, Optional


NetworkSource = Schema({
    "id": int,
    "plc_block_id": int,
    Optional("title", default=""): str,
    Optional("comment", default=""): str,
})

Parameter = Schema({
    "plc_block_id": int,
    "parameters": {str: str},
})
