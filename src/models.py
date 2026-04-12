import os
from gi.repository import GdkPixbuf

class SteamGame:
    
    def __init__(self, appid, name, pfx, icon_path=None):
        self.appid = appid
        self.name = name
        self.pfx = pfx
        self.icon_path = icon_path
        self.icon_pixbuf = None

    def load_icon(self, size=48):
        if self.icon_pixbuf:
            return self.icon_pixbuf

        if self.icon_path and os.path.exists(self.icon_path):
            try:
                self.icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    self.icon_path,size,size
                )
                return self.icon_pixbuf
            except Exception as e:
                print(f"Failed to load icon for {self.name}: {e}")

        return None


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
        
