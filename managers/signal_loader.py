from abc import ABC, abstractmethod
import pandas as pd
from models.signal import Signal

# Interface that describes how signal loaders should be implemented
class ISignalLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Signal:
        pass


class TextSignalLoader(ISignalLoader):
    def load(self, file_path: str) -> Signal:
        data = pd.read_csv(file_path, sep=',',nrows=1000)
        x = data.iloc[:, 0].values
        y = data.iloc[:, 1].values
        return Signal(x, y)
    
class CSVSignalLoader(ISignalLoader):
    def load(self, file_path: str) -> Signal:
        data = pd.read_csv(file_path, skiprows=2,nrows=1000)
        x = data.iloc[:, 0].values
        y = data.iloc[:, 1].values
        return Signal(x, y)

class ExcelXSignalLoader(ISignalLoader):
    def load(self, file_path: str) -> Signal:
        data = pd.read_excel(file_path, header=None,nrows=1000)
        x = data.iloc[:, 0].values
        y = data.iloc[:, 1].values
        return Signal(x, y)
    
class ExcelSignalLoader(ISignalLoader):
    def load(self, file_path: str) -> Signal:
        data = pd.read_excel(file_path, header=None, engine="xlrd",nrows=1000)
        x = data.iloc[:, 0].values
        y = data.iloc[:, 1].values
        return Signal(x, y)