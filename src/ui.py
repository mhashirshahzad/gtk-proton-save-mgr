import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
import os
import subprocess
import variables


# ---------------- Utils ----------------

def split_paths(raw):
    if isinstance(raw, str):
        return [p for p in raw.split(" ") if p.strip()]
    return raw


def open_path(path):
    subprocess.Popen(["xdg-open", os.path.expanduser(path)])


# ---------------- Sidebar ----------------

class Sidebar(Gtk.Box):
    def __init__(self, on_select):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.on_select = on_select

        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        self.add_btn("Steam", "steam")
        self.add_btn("Non-Steam", "nonsteam")
        self.add_btn("Lutris", "lutris")
        self.add_btn("Prefixes", "prefixes")

    def add_btn(self, label, key):
        btn = Gtk.Button(label=label)
        btn.set_hexpand(True)
        btn.set_halign(Gtk.Align.FILL)
        btn.add_css_class("flat")
        btn.connect("clicked", lambda *_: self.on_select(key))
        self.append(btn)


# ---------------- Card ----------------

class Card(Gtk.Box):
    def __init__(self, title):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class("card")

        # TRUE FIXED HEIGHT
        self.set_size_request(-1, 84)
        self.set_vexpand(False)
        self.set_hexpand(True)
        self.set_valign(Gtk.Align.START)
        self.set_overflow(Gtk.Overflow.HIDDEN)

        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

        # ---------------- TITLE ----------------
        self.title = Gtk.Label(label=title, xalign=0)
        self.title.add_css_class("title-4")
        self.title.set_margin_start(6)
        self.title.set_margin_top(6)
        self.title.set_hexpand(True)
        self.title.set_vexpand(False)

        self.append(self.title)

        # ---------------- SPACER (pushes buttons down) ----------------
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)

        # ---------------- BUTTON ROW ----------------
        self.actions = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            homogeneous=True   # IMPORTANT: equal width buttons
        )

        self.actions.set_margin_start(6)
        self.actions.set_margin_end(6)
        self.actions.set_margin_bottom(6)

        self.actions.set_hexpand(True)
        self.actions.set_vexpand(False)
        self.actions.set_valign(Gtk.Align.END)

        self.append(self.actions)

    def add_action(self, label, callback):
        btn = Gtk.Button(label=label)
        btn.add_css_class("flat")

        # fill evenly because homogeneous=True
        btn.set_hexpand(True)
        btn.set_vexpand(False)

        btn.connect("clicked", callback)
        self.actions.append(btn)

# ---------------- Game / Prefix Cards ----------------

class GameCard(Card):
    def __init__(self, title, pfx_paths):
        super().__init__(title)

        for p in split_paths(pfx_paths):
            self.add_action(p, lambda _, path=p: open_path(path))


class PrefixCard(Card):
    def __init__(self, name, paths):
        super().__init__(name)

        for p in split_paths(paths):
            self.add_action(p, lambda _, path=p: open_path(path))


# ---------------- Views ----------------

class GameListView(Gtk.ScrolledWindow):
    def __init__(self, games, kind="steam"):
        super().__init__()
        self.set_vexpand(True)

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.box.set_margin_top(10)
        self.box.set_margin_bottom(10)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)

        self.set_child(self.box)

        self.games = games
        self.kind = kind
        self.render(games)

    def render(self, games):
        for c in list(self.box):
            self.box.remove(c)

        for game in games:
            if self.kind == "lutris":
                self.box.append(GameCard(game.name, game.pfx))
            else:
                self.box.append(GameCard(
                    f"{game.name} ({game.appid})",
                    game.pfx
                ))


class PrefixView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.append(PrefixCard("Wine", "~/.wine"))
        self.append(PrefixCard("UMU", "~/Games/umu/umu-default/"))
        self.append(PrefixCard("Lutris", "~/Games/"))


# ---------------- Main Window ----------------

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(950, 600)
        self.set_title("Proton Save Manager")

        # -------- Data --------
        self.data = {
            "steam": variables.steam_games,
            "nonsteam": variables.non_steam_games,
            "lutris": variables.lutris_games,
        }

        # -------- Pages --------
        self.steam_view = GameListView(self.data["steam"], "steam")
        self.nonsteam_view = GameListView(self.data["nonsteam"], "nonsteam")
        self.lutris_view = GameListView(self.data["lutris"], "lutris")
        self.prefix_view = PrefixView()

        # -------- Stack --------
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)

        self.stack.add_named(self.steam_view, "steam")
        self.stack.add_named(self.nonsteam_view, "nonsteam")
        self.stack.add_named(self.lutris_view, "lutris")
        self.stack.add_named(self.prefix_view, "prefixes")

        # -------- Sidebar --------
        sidebar = Sidebar(self.on_nav)

        sidebar_page = Adw.NavigationPage()
        sidebar_page.set_child(sidebar)
        sidebar_page.set_title("Library")

        content_page = Adw.NavigationPage()
        content_page.set_child(self.stack)
        content_page.set_title("Games")

        split = Adw.NavigationSplitView()
        split.set_sidebar(sidebar_page)
        split.set_content(content_page)

        # -------- Search --------
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search games...")
        self.search.connect("search-changed", self.on_search)
        self.search.set_visible(True)

        # -------- Header --------
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Proton Save Manager"))
        header.pack_end(self.search)

        # -------- Root --------
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(split)

        self.set_content(toolbar)

    # ---------------- Navigation ----------------

    def on_nav(self, key):
        self.stack.set_visible_child_name(key)

        # search only for steam
        self.search.set_visible(key == "steam")

    # ---------------- Search ----------------

    def on_search(self, entry):
        q = entry.get_text().lower().strip()

        def match(g):
            if not q:
                return True
            return (
                q in g.name.lower()
                or q in getattr(g, "appid", "")
                or q in getattr(g, "exe", "")
            )

        self.steam_view.render([g for g in self.data["steam"] if match(g)])
        self.nonsteam_view.render([g for g in self.data["nonsteam"] if match(g)])
        self.lutris_view.render([g for g in self.data["lutris"] if match(g)])


# ---------------- App ----------------

class GameApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.bongo.protonsavemgr")

    def do_activate(self):
        win = MainWindow(self)
        win.present()


def run():
    Adw.init()
    app = GameApp()
    app.run(None)
