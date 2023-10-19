
from PyQt6 import QtCore, QtWidgets
from managers.signal_loader import ISignalLoader, TextSignalLoader, CSVSignalLoader, ExcelXSignalLoader, ExcelSignalLoader
from models.signal import Signal

def get_signal_from_file(app):
        # get path of signal files only of types (xls, csv, txt)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(app, 'Single File', QtCore.QDir.rootPath(), "(*.csv);;(*.txt);;(*.xls);;(*.xlsx)")
        if not file_path:
            return None
        # check the type of signal file
        file_type = file_path.split('.')[-1]

        # Picking the right loader from file_type
        loader: ISignalLoader
        if file_type == 'xls':
            loader = ExcelSignalLoader()
        elif file_type == 'xlsx':
            loader = ExcelXSignalLoader()
        elif file_type == 'csv':
            loader = CSVSignalLoader()
        else:
            loader = TextSignalLoader()
        
        signal: Signal = loader.load(file_path)
        return signal