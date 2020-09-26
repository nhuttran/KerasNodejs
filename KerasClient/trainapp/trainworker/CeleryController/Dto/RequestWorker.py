from .ParseJson import ParseJsonDto

class AuthTrainDto(ParseJsonDto):
    ftpHost = None
    ftpPort = None
    ftpUserId = None
    ftpPassword = None
    downloadPathFile = None
    uploadPath = None

    def __init__(self, ftpHost, ftpPort, ftpUserId, ftpPassword, downloadPathFile, uploadPath, *args, **kwargs):
        self.ftpHost = ftpHost
        self.ftpPort = ftpPort
        self.ftpUserId = ftpUserId
        self.ftpPassword = ftpPassword
        self.downloadPathFile = downloadPathFile
        self.uploadPath = uploadPath

class RequestWorkerDto(ParseJsonDto):
    userId = None
    trainKbn = None
    classLabels = None
    epochs = None
    trainFaces = None
    labels = None

    def __init__(self, userId, trainKbn, classLabels, epochs, trainFaces, labels, *args, **kwargs):
        super().__init__()
        self.userId = userId
        self.trainKbn = trainKbn
        self.classLabels = classLabels
        self.epochs = epochs
        self.trainFaces = trainFaces
        self.labels = labels
