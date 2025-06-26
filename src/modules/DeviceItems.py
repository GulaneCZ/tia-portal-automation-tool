from __future__ import annotations
from dataclasses import dataclass
import logging

from src.core import logs

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class DeviceItem:
    DeviceID: int
    typeIdentifier: str
    name: str
    positionNumber: int



def plug_new(data: DeviceItem, device: Siemens.Engineering.HW.Device, slots_required: int):
    hw_object: Siemens.Engineering.HW.HardwareObject = device.DeviceItems[0]

    logger.info(f"Plugging of Device Item {data.typeIdentifier} on position [{data.positionNumber + slots_required}] started")

    if hw_object.CanPlugNew(data.typeIdentifier, data.name, data.positionNumber + slots_required):
        hw_object.PlugNew(data.typeIdentifier, data.name, data.positionNumber + slots_required)

        logger.info(f"Plugged Device Item {data.typeIdentifier} on position [{data.positionNumber + slots_required}]")

        return

    logging.info(f"{data.typeIdentifier} not plugged")

    return

