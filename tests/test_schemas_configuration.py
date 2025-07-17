from pathlib import Path
import json
import pytest

from src.schemas import configuration

BASE_DIR = Path(__file__).parent

all = BASE_DIR / "configs" / "all.json"
one_device = BASE_DIR / "configs" / "one_device.json"
one_device_with_local_modules = BASE_DIR / "configs" / "one_device_with_local_modules.json"
multiple_devices = BASE_DIR / "configs" / "multiple_devices.json"
multiple_devices_with_libraries = BASE_DIR / "configs" / "multiple_devices_with_libraries.json"
multiple_devices_with_plc_data_types = BASE_DIR / "configs" / "multiple_devices_with_plc_data_types.json"

def test_json_config():
    with open(one_device) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None

    with open(multiple_devices) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None

    with open(one_device_with_local_modules) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None

    with open(multiple_devices_with_libraries) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None

    with open(multiple_devices_with_plc_data_types) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None

    with open(all) as file:
        config = json.load(file)
        assert configuration.validate(config) is not None
