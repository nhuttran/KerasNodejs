import json
from .ParseJson import ParseJsonDto

class LoginAuthDto(ParseJsonDto):
    authKey = None
    loginId = None
    utcTime = None

    def __init__(self, authKey, loginId, utcTime, *args, **kwargs):
        super().__init__()
        self.authKey = authKey
        self.loginId = loginId
        self.utcTime = utcTime
