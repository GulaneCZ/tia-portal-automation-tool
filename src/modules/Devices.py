from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging

from src.core import logs
import src.modules.Networks as Networks

logs.setup(logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class Device:
    p_typeIdentifier: str
    p_name: str
    p_deviceName: str
    ID: int
    SlotsRequired: int
    NetworkInterface: Optional[NetworkInterface] = None


def create(data: list[Device], project: Siemens.Engineering.Project) -> list[Siemens.Engineering.HW.Device]:
    devices: list[Siemens.Engineering.HW.Device] = []

    for device_data in data:
        device_composition: Siemens.Engineering.HW.DeviceComposition = project.Devices
        device: Siemens.Engineering.HW.Device = device_composition.CreateWithItem(device_data.p_typeIdentifier, device_data.p_name, device_data.p_deviceName)

        logger.info(f"Created Device ({device_data.p_deviceName}, {device_data.p_typeIdentifier}) on {device.Name}")

        devices.append(device)

    return devices

def get_plc_software(imports:Imports, device: Siemens.Engineering.HW.Device) -> Siemens.Engineering.HW.Software:
    SE: Siemens.Engineering = imports.DLL

    hw_obj: Siemens.Engineering.HW.HardwareObject = device.DeviceItems

    for device_item in hw_obj:
        logger.debug(f"Accessing a PlcSoftware from Device Item {device_item.Name}")

        software_container: Siemens.Engineering.HW.Features.SoftwareContainer = SE.IEngineeringServiceProvider(device_item).GetService[SE.HW.Features.SoftwareContainer]()

        if not software_container:
            logger.debug(f"No Software Container for Device Item {device_item.Name}")
            continue

        plc_software: Siemens.Engineering.HW.Software = software_container.Software
        if not isinstance(plc_software, SE.SW.PlcSoftware):
            logger.debug(f"No PlcSoftware found for Device Item {device_item.Name}")
            continue

        logger.debug(f"Found PlcSoftware for Device Item {device_item.Name}")
        return plc_software
