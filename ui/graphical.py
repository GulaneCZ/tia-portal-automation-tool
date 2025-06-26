from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from pathlib import Path
from ui.qt6.app import Ui_MainWindow
import json
import logging

from src.core import core
from src.core import logs
from src.schemas import configuration
import src.modules.Portals as Portals


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        logs.setup(logging.INFO, textbox=self.ui.textbrowser_logs)

        self.logger = logging.getLogger(__name__)
        self.logger.info("Application started.")

        self.project_json: dict = {}
        self.library_filepath: Path = Path()
        self.dlls: dict[str, Path] = core.generate_dlls()
        self.settings: dict = {
            "enable_ui": self.ui.checkBox_enable_ui.isChecked(),
        }

        self._generate_dlls()
        self.version: str = self.ui.combobox_dll_versions.currentText()
        self.logger.info(f"Current version selected: {self.version}")


        # Butons
        self.ui.button_import.clicked.connect(self.import_file)
        self.ui.button_select_library.clicked.connect(self.select_library)
        self.ui.button_execute_portal.clicked.connect(self.execute)
        self.ui.combobox_dll_versions.currentTextChanged.connect(self.change_version)
        self.ui.checkBox_enable_ui.toggled.connect(self.toggle_enable_ui)
        self.ui.checkbox_allow_overwrite.toggled.connect(self.toggle_overwrite)
        self.ui.actionImport.triggered.connect(self.import_file)
        self.ui.actionExit.triggered.connect(lambda: QApplication.quit())

        
    def execute(self):
        if not self.project_json:
            self.logger.error(f"Invalid project")
            return
        import clr
        from System.IO import DirectoryInfo, FileInfo
        dll = self.dlls.get(self.version)
        if not dll:
            self.logger.error(f"Invalid version selected")
            return
        clr.AddReference(dll.as_posix())
        import Siemens.Engineering as SE

        imports = Portals.Imports(SE, DirectoryInfo, FileInfo)
        self.logger.info(f"Creating project: {self.project_json['name']}")
        core.execute(imports, self.project_json, self.settings)

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON Config", "", "JSON Files (*.json)")
        if file_path:
            file_path: Path = Path(file_path)
            with open(file_path) as json_file:
                loaded_json = json.load(json_file)
                try:
                    self.project_json = configuration.validate(loaded_json)
                    self.ui.label_json_filepath.setText(file_path.name)
                    self.project_json['directory'] = file_path.absolute().parent
                    self.project_json['name'] = file_path.stem
                    self.project_json['overwrite'] = self.ui.checkbox_allow_overwrite.isChecked()
                    self.logger.info(f"Imported Json Config: {file_path}")
                except:
                    self.logger.error(f"Invalid project config! Did not validate: {file_path}")
                    self.ui.label_json_filepath.setText("INVALID CONFIG!")

    def change_version(self, text: str):
        self.version = text
        self.logger.info(f"Current version selected: {self.version}")


    def select_library(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Library", "", "Global library (*.al*)|*.al*")
        if file_path:
            self.library_filepath = Path(file_path)

            if not self.project_json: return
            self.ui.label_library_path.setText(self.library_filepath.stem)
            self.project_json['libraries'] = [{"path": self.library_filepath}]
            self.logger.info(f"Selected Global Library: {self.library_filepath}")

    def toggle_enable_ui(self, checked: bool):
        self.settings['enable_ui'] = checked
        if checked:
            self.logger.info(f"TIA Portal will show User Interface.")
        else:
            self.logger.info(f"TIA Portal will now run in the background.")

    def toggle_overwrite(self, checked: bool):
        if not self.project_json:
            return

        self.project_json['overwrite'] = checked
        if checked:
            self.logger.info(f"TIA Portal will OVERWRITE exsting project.")
        else:
            self.logger.info(f"TIA Portal will NOT OVERWRITE existing project.")

    def _generate_dlls(self):
        for dll_name in self.dlls:
            self.ui.combobox_dll_versions.addItem(dll_name)
            self.logger.info(f"Finished compiling API: {self.dlls[dll_name]}")


app = QApplication()
