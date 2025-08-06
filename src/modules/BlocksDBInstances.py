from dataclasses import dataclass
from enum import Enum

from src.modules.BlocksDatabase import Database


class CallOptionEnum(Enum):
    Single = "Single"
    Multi = "Multi"
    Parameter = "Parameter"


@dataclass
class Instance(Database):
    CallOption: CallOptionEnum


# @dataclass
# class SingleInstance(Database):
#     CallOption: CallOptionEnum
#
#
# @dataclass
# class MultiInstance(Database):
#     CallOption: CallOptionEnum
#
#
# @dataclass
# class ParameterInstance(Database):
#     CallOption: CallOptionEnum
