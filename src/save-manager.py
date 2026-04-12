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
LIBRARYCACHE_PATH = os.path.join(STEAM_PATH, "appcache", "librarycache")

# -------- Steam Icon --------

def get_steam_icon_path(appid):
    """
    Get the full path to a game's icon by finding any JPG in the librarycache folder.
    """
    icon_dir = os.path.join(LIBRARYCACHE_PATH, str(appid))
    
    if not os.path.exists(icon_dir):
        return None
    
    # Look for any .jpg file in the directory
    for file in os.listdir(icon_dir):
        if file.endswith('.jpg'):
            icon_path = os.path.join(icon_dir, file)
            print(f"Found icon for appid {appid}: {file}")  # Debug
            return icon_path
    
    print(f"No icon found for appid {appid} in {icon_dir}")  # Debug
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
            
            # Get icon path by looking for any JPG in the cache folder
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
