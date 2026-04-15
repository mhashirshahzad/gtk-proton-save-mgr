import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf
import os

class SteamGame:
    def __init__(self, appid, name, pfx, icon_path=None):
        self.appid = appid
        self.name = name
        self.pfx = pfx
        self.icon_path = icon_path
        self.icon_pixbuf = None
    
    def load_icon(self, size=64):
        """Load icon as GdkPixbuf.Pixbuf for GTK display."""
        if self.icon_pixbuf:
            return self.icon_pixbuf
    
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                # Get original image dimensions
                original = GdkPixbuf.Pixbuf.new_from_file(self.icon_path)
            
                # Don't upscale if original is smaller than requested
                self.icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    self.icon_path, original.get_width(), original.get_height()
                )

                print(f"Loading icon size for {self.name}: {original.get_width()}x{original.get_height()}")
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
