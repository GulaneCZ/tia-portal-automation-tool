from pathlib import Path
import json

from src.core import core
from src.schemas import configuration
import src.modules.Portals as Portals

BASE_DIR = Path(__file__).parent

multiple_devices = BASE_DIR / "configs" / "multiple_devices.json"
multiple_devices_with_libraries = BASE_DIR / \
    "configs" / "multiple_devices_with_libraries.json"
multiple_devices_with_local_modules = BASE_DIR / \
    "configs" / "multiple_devices_with_local_modules.json"
multiple_devices_with_plc_data_types = BASE_DIR / \
    "configs" / "multiple_devices_with_plc_data_types.json"
plc_tags = BASE_DIR / "configs" / "plc_tags.json"
global_dbs = BASE_DIR / "configs" / "global_dbs.json"
organization_blocks = BASE_DIR / "configs" / "organization_blocks.json"
function_blocks = BASE_DIR / "configs" / "function_blocks.json"
functions = BASE_DIR / "configs" / "functions.json"


dlls = core.generate_dlls()
dll = dlls['V18']
import clr  # noqa: E402
from System.IO import DirectoryInfo, FileInfo  # noqa: E402
clr.AddReference(dll.as_posix())
import Siemens.Engineering as SE  # noqa: E402

imports = Portals.Imports(SE, DirectoryInfo, FileInfo)


def test_core():
    config = None
    with open(multiple_devices) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{multiple_devices.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_local_modules():
    config = None
    with open(multiple_devices_with_local_modules) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{multiple_devices_with_local_modules.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_plc_tags():
    config = None
    with open(plc_tags) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{plc_tags.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_libraries():
    config = None
    with open(multiple_devices_with_libraries) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{multiple_devices_with_libraries.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_plc_data_types():
    config = None
    with open(multiple_devices_with_plc_data_types) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{multiple_devices_with_plc_data_types.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_globaldb():
    config = None
    with open(global_dbs) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{global_dbs.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_organization_block():
    config = None
    with open(organization_blocks) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{organization_blocks.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_function_block():
    config = None
    with open(function_blocks) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{function_blocks.stem}"

    core.execute(imports, config, {"enable_ui": True, })


def test_core_function():
    config = None
    with open(functions) as file:
        config = configuration.validate(json.load(file))
    config['directory'] = BASE_DIR.parent.parent.parent
    config['name'] = f"test_core.{functions.stem}"

    core.execute(imports, config, {"enable_ui": True, })
