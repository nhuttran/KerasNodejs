import json
from .ParseJson import ParseJsonDto

class TrainResultDto(ParseJsonDto):
    jsonFile = None
    h5File = None
    mlFile = None
    startTime = None
    endTime = None
    totalTime = None
    errorRate = None
    accuracyRate = None

    def __init__(self, jsonFile, h5File, mlFile, startTime, endTime, totalTime, errorRate, accuracyRate, *args, **kwargs):
        super().__init__()
        self.jsonFile = jsonFile
        self.h5File = h5File
        self.mlFile = mlFile
        self.startTime = startTime
        self.endTime = endTime
        self.totalTime = totalTime
        self.errorRate = errorRate
        self.accuracyRate = accuracyRate
