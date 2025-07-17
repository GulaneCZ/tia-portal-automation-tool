from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from src.modules.XML.Documents import Document
from src.modules.XML.ProgramBlocks import ProgramBlock

class FC(Base):
    DOCUMENT = "SW.Blocks.FC"
    def __init__(self, data: ProgramBlock) -> None:
        super().__init__(data.Name, data.Number, data.ProgrammingLanguage)

        self._create_input_section()
        self._create_output_section()
        self._create_inout_section()
        self._create_temp_section()
        self._create_constant_section()
        self._create_return_section()
