import enum

class ProcessStatus(enum.Enum):
    OPTIMIZER_SETUP = 0
    FORKING_PROCESS = enum.auto()
    EXECUTING_QPROP = enum.auto()
    EXTRACTING_DATA = enum.auto()
    ITERATING_STATE = enum.auto()
    UPDATING_COUNTS = enum.auto()
    CHECKING_LIMITS = enum.auto()
    SUCCESS_TAKEOFF = enum.auto()
    FAILED_VELOCITY = enum.auto()
    
    @classmethod
    def get(cls, index: int):
        return list(cls)[index]
