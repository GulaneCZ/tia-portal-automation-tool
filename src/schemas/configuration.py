from __future__ import annotations
from schema import Schema, And, Or, Optional

from src.schemas.BlocksDBInstances import SingleInstance, MultiInstance
from src.schemas.BlocksData import GlobalDB
from src.schemas.BlocksFB import FunctionBlock
from src.schemas.BlocksFC import Function
from src.schemas.BlocksOB import OrganizationBlock
from src.schemas.DeviceItems import DeviceItem
from src.schemas.Devices import PLC
from src.schemas.Libraries import GlobalLibrary
from src.schemas.NetworkSources import NetworkSource, WireTemplate, WireParameter
from src.schemas.PlcDataTypes import PlcDataType
from src.schemas.PlcTags import PlcTagTable
from src.schemas.ProgramBlocks import PlcBlock, VariableSection

root = Schema(
    {
        Optional("overwrite", default=True): bool,
        Optional("devices", default=[]): And(list, [Or(PLC)]),
        Optional("Local modules", default=[]): And(list, [DeviceItem]),
        Optional("PLC tags", default=[]): And(list, [PlcTagTable]),
        Optional("PLC data types", default=[]): And(list, [PlcDataType]),
        Optional("Wire template", default=[]): And(list, [WireTemplate]),
        Optional("libraries", default=[]): And(list, [GlobalLibrary]),
        Optional("Program blocks", default=[]): And(list, [Or(
            PlcBlock,  # Used for Instance Blocks
            OrganizationBlock, FunctionBlock, Function,
            GlobalDB
        )]),
        Optional("Network sources", default=[]): And(list, [NetworkSource]),
        Optional("Variable sections", default=[]): And(list, [
            VariableSection
        ]),
        Optional("Instances", default=[]): And(list, [Or(
            SingleInstance,
            MultiInstance
        )]),
        Optional("Wire parameters", default=[]): And(list, [WireParameter]),
    },
    ignore_extra_keys=True
)


def validate(data):
    return root.validate(data)
