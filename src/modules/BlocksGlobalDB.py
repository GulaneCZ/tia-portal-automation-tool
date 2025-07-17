from dataclasses import dataclass

from src.modules.XML.ProgramBlocks import VariableSection, Database

@dataclass
class GlobalDB(Database):
    VariableSections: list[VariableSection]
    Attributes: dict
