class SteamGame:
    def __init__(self, appid, name, pfx):
        self.appid = appid
        self.name = name
        self.pfx = pfx


class LutrisGame:
    def __init__(self, name, exe, pfx):
        self.name = name
        self.exe = exe
        self.pfx = pfx


class NonSteamGame:
    def __init__(self, name, appid, pfx):
        self.name = name
        self.appid = appid
        self.pfx = pfx
