import re
import yaml
import os
from pathlib import Path
import vdf

import variables
from models import SteamGame, LutrisGame, NonSteamGame
import ui

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
    data = read_vdf("~/.local/share/Steam/config/libraryfolders.vdf")

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

            variables.steam_games.append(
                SteamGame(appid, name, get_pfx_paths(appid)))


def load_lutris():
    path = os.path.expanduser("~/.local/share/lutris/games/")
    if not os.path.exists(path):
        return

    for file in os.listdir(path):
        with open(os.path.join(path, file)) as f:
            data = yaml.safe_load(f)

        name = re.sub(r"-\d+$", "", Path(file).stem)
        exe = data.get("game", {}).get("exe", "")
        prefix = data.get("game", {}).get("prefix", "")

        variables.lutris_games.append(LutrisGame(name, exe, prefix))


def load_nonsteam():
    base = os.path.expanduser("~/.local/share/Steam/userdata/")
    if not os.path.exists(base):
        return

    for user in os.listdir(base):
        shortcuts = os.path.join(base, user, "config/shortcuts.vdf")
        if not os.path.exists(shortcuts):
            continue

        with open(shortcuts, "rb") as f:
            data = vdf.binary_load(f)

        for entry in data["shortcuts"].values():
            name = entry.get("AppName")
            appid = entry.get("appid")
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
