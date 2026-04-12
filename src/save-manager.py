import re
import yaml
import os
from pathlib import Path
import vdf

import variables
from models import SteamGame, LutrisGame, NonSteamGame
import ui

# -------- Constants --------

STEAM_PATH = os.path.expanduser("~/.local/share/Steam")
APPCACHE_PATH = os.path.join(STEAM_PATH, "appcache")
APPINFO_PATH = os.path.join(APPCACHE_PATH, "appinfo.vdf")
LIBRARYCACHE_PATH = os.path.join(APPCACHE_PATH, "librarycache")

# -------- Steam Icon --------

def get_icon_hash_from_appinfo(appid):
    """
    Extract icon hash for a game from local appinfo.vdf.
    Returns the hash string or None if not found.
    """
    if not os.path.exists(APPINFO_PATH):
        return None
    
    try:
        # Parse the binary VDF file
        with open(APPINFO_PATH, "rb") as f:
            data = vdf.binary_load(f)
        
        # Navigate to the app's icon hash
        # Structure: data[appid]["common"]["icon"]
        app_data = data.get(str(appid))
        if app_data and "common" in app_data:
            common = app_data["common"]
            if "icon" in common:
                return common["icon"]
            # Some games use "clienticon" instead
            if "clienticon" in common:
                return common["clienticon"]
    except Exception as e:
        print(f"Error parsing appinfo.vdf for {appid}: {e}")
    
    return None

def get_steam_icon_path(appid):
    """
    Get the full path to a game's icon using local appinfo.vdf.
    """
    # First, get the icon hash from appinfo.vdf
    icon_hash = get_icon_hash_from_appinfo(appid)
    
    if not icon_hash:
        return None
    
    # Construct the icon path
    icon_path = os.path.join(
        LIBRARYCACHE_PATH,
        str(appid), 
        f"{icon_hash}.jpg"
    )
    
    if os.path.exists(icon_path):
        return icon_path
    
    # Fallback: try to find any jpg in the directory
    icon_dir = os.path.join(LIBRARYCACHE_PATH, str(appid))
    if os.path.exists(icon_dir):
        for file in os.listdir(icon_dir):
            if file.endswith('.jpg'):
                return os.path.join(icon_dir, file)
    
    return None


# -------- Data Loaders --------

def read_vdf(path):
    with open(os.path.expanduser(path), encoding="utf-8") as f:
        return vdf.parse(f)


def get_pfx_paths(appid):
    paths = []
    for folder in variables.library_folders:
        p = os.path.join(folder, f"steamapps/compatdata/{appid}")
        if os.path.exists(p):
            paths.append(f"file://{p}")
    return " ".join(paths)


def load_steam():
    data = read_vdf(os.path.join(STEAM_PATH, "config/libraryfolders.vdf"))

    for _, value in data["libraryfolders"].items():
        variables.library_folders.append(value.get("path"))

    for folder in variables.library_folders:
        steamapps = os.path.join(folder, "steamapps")
        if not os.path.exists(steamapps):
            continue

        for f in os.listdir(steamapps):
            if "appmanifest" not in f:
                continue

            manifest = read_vdf(os.path.join(steamapps, f))
            appid = manifest["AppState"]["appid"]
            name = manifest["AppState"]["name"]
            
            # Get icon path
            icon_path = get_steam_icon_path(appid)

            variables.steam_games.append(
                SteamGame(appid, name, get_pfx_paths(appid), icon_path))


def load_lutris():
    lutris_path = os.path.expanduser("~/.local/share/lutris/games/")
    if not os.path.exists(lutris_path):
        return

    for file in os.listdir(lutris_path):
        with open(os.path.join(lutris_path, file)) as f:
            data = yaml.safe_load(f)

        name = re.sub(r"-\d+$", "", Path(file).stem)
        exe = data.get("game", {}).get("exe", "")
        prefix = data.get("game", {}).get("prefix", "")

        variables.lutris_games.append(LutrisGame(name, exe, prefix))


def load_nonsteam():
    userdata_path = os.path.join(STEAM_PATH, "userdata")
    if not os.path.exists(userdata_path):
        return

    for user in os.listdir(userdata_path):
        shortcuts = os.path.join(userdata_path, user, "config/shortcuts.vdf")
        if not os.path.exists(shortcuts):
            continue

        with open(shortcuts, "rb") as f:
            data = vdf.binary_load(f)

        for entry in data["shortcuts"].values():
            name = entry.get("AppName")
            appid = entry.get("appid")

            # signed and unsigned magic
            # some appids are negative
            # so using this we can convert them into positive
            # and get the actual path
            u_appid = appid & 0xFFFFFFFF

            variables.non_steam_games.append(
                NonSteamGame(name, appid, get_pfx_paths(u_appid)))


# -------- Main --------

def load_all():
    load_steam()
    load_nonsteam()
    load_lutris()


if __name__ == "__main__":
    load_all()
    ui.run()
