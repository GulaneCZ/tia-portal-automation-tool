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


def find_all(TIA: Siemens.Engineering.TiaPortal, name: str) -> list[Siemens.Engineering.HW.DeviceItem]:
    devices: list[Siemens.Engineering.HW.DeviceItem] = []

    for device_composition in TIA.Projects[0].Devices:
        for device in device_composition.DeviceItems:
            if device.Name == name:
                devices.append(device)

    return devices


def find(TIA: Siemens.Engineering.TiaPortal, name: str) -> Siemens.Engineering.HW.DeviceItem:
    devices = find_all(TIA, name)
    return devices[0]


def plug_new(data: DeviceItem, device: Siemens.Engineering.HW.Device, slots_required: int):
    hw_object: Siemens.Engineering.HW.HardwareObject = device.DeviceItems[0]

    logger.info(f"Plugging of Device Item {data.typeIdentifier} on position [{
                data.positionNumber + slots_required}] started")

    if hw_object.CanPlugNew(data.typeIdentifier, data.name, data.positionNumber + slots_required):
        hw_object.PlugNew(data.typeIdentifier, data.name,
                          data.positionNumber + slots_required)

        logger.info(f"Plugged Device Item {data.typeIdentifier} on position [{
                    data.positionNumber + slots_required}]")

        return

    logging.info(f"{data.typeIdentifier} not plugged")

    return
