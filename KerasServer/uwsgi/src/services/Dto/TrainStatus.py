import json
from .ParseJson import ParseJsonDto

class TrainStatusDto(ParseJsonDto):
    trainKbn = None
    status = None
    epochs = None
    currentEpoch = None

    def __init__(self, trainKbn, status, epochs, currentEpoch, *args, **kwargs):
        super().__init__()
        self.trainKbn = trainKbn
        self.status = status
        self.epochs = epochs
        self.currentEpoch = currentEpoch
