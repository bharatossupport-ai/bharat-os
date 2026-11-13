#!/usr/bin/env python3
"""BharatOS Companion AI — a local, offline assistant that operates the PC.

Talks to a local Ollama server (default model: qwen3.5:4b) using native tool
calling. The model plans; this file executes tools on the user's desktop.
Human stays in control: Autopilot can be switched to "Ask me first", every
risky step asks for confirmation, and Esc stops the current task.
"""
import json, os, shlex, subprocess, sys, threading, pathlib, shutil, platform, datetime
import requests
from PyQt6 import QtCore, QtGui, QtWidgets, QtNetwork

APP_ID = "bharatos-companion"
CFG_DIR = pathlib.Path.home() / ".config" / "bharatos"
CFG_FILE = CFG_DIR / "companion.json"
DEFAULTS = {"model": "qwen3.5:4b", "ollama": "http://127.0.0.1:11434",
            "autopilot": False, "tone": "warm", "language": "en", "max_steps": 8}
HOME = pathlib.Path.home()

def load_cfg():
    try:
        return {**DEFAULTS, **json.loads(CFG_FILE.read_text())}
    except Exception:
        return dict(DEFAULTS)

def save_cfg(cfg):
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    CFG_FILE.write_text(json.dumps(cfg, indent=2))

# ---------------------------------------------------------------- tools
APPS = {"files": "dolphin", "file manager": "dolphin", "browser": "firefox-esr",
        "firefox": "firefox-esr", "terminal": "konsole", "editor": "kate",
        "code": "kate", "settings": "systemsettings", "writer": "libreoffice --writer",
        "calc": "libreoffice --calc", "spreadsheet": "libreoffice --calc",
        "slides": "libreoffice --impress", "music": "vlc", "video": "vlc",
        "photos": "gwenview", "pdf": "okular", "screenshot": "spectacle", "store": "plasma-discover", "app store": "plasma-discover"}
SERVICES = {"digilocker": "https://www.digilocker.gov.in", "umang": "https://web.umang.gov.in",
            "irctc": "https://www.irctc.co.in", "upi": "https://www.npci.org.in"}

def _safe(path):
    p = (HOME / path).expanduser().resolve() if not str(path).startswith("/") else pathlib.Path(path).resolve()
    return p

def t_open_app(name):
    cmd = APPS.get(name.lower().strip(), name)
    if not shutil.which(cmd.split()[0]):
        return f"App '{name}' is not installed."
    subprocess.Popen(shlex.split(cmd), start_new_session=True)
    return f"Opened {name}."

def t_open_url(url):
    url = SERVICES.get(url.lower().strip(), url)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    subprocess.Popen(["xdg-open", url], start_new_session=True)
    return f"Opened {url} in the browser."

def t_web_search(query):
    import urllib.parse
    return t_open_url("https://duckduckgo.com/?q=" + urllib.parse.quote(query))

def t_list_files(path="."):
    p = _safe(path)
    if not p.exists():
        return f"{p} does not exist."
    items = sorted(p.iterdir())[:200]
    return "\n".join(("[dir] " if i.is_dir() else "") + i.name for i in items) or "(empty)"

def t_read_file(path):
    p = _safe(path)
    return p.read_text(errors="replace")[:8000]

def t_write_file(path, content):
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} characters to {p}."

def t_create_folder(path):
    p = _safe(path); p.mkdir(parents=True, exist_ok=True)
    return f"Created folder {p}."

def t_move_file(src, dst):
    shutil.move(str(_safe(src)), str(_safe(dst)))
    return f"Moved {src} to {dst}."

def t_run_command(command):
    r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120, cwd=HOME)
    out = (r.stdout + r.stderr)[-4000:]
    return f"exit {r.returncode}\n{out}"

def t_type_text(text):
    subprocess.run(["xdotool", "type", "--delay", "15", text])
    return "Typed the text."

def t_press_keys(keys):
    subprocess.run(["xdotool", "key"] + keys.split())
    return f"Pressed {keys}."

def t_system_info():
    du = shutil.disk_usage(HOME)
    mem = open("/proc/meminfo").read().split("\n")[:3]
    return (f"{platform.platform()}\nTime: {datetime.datetime.now():%a %d %b %Y %I:%M %p}\n"
            f"Disk free: {du.free//2**30} GB of {du.total//2**30} GB\n" + "\n".join(mem))

def t_set_volume(percent):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(percent)}%"])
    return f"Volume set to {percent}%."

def t_install_app(name):
    r = subprocess.run(["flatpak", "search", "--columns=application", name], capture_output=True, text=True)
    ids = [l.strip() for l in r.stdout.splitlines() if "." in l]
    if not ids:
        return f"No app called {name} in the store."
    r = subprocess.run(["flatpak", "install", "-y", "--user", "flathub", ids[0]], capture_output=True, text=True, timeout=1800)
    return f"Installed {ids[0]}." if r.returncode == 0 else r.stderr[-1500:]

def t_run_windows_app(path):
    subprocess.Popen(["bharatos-run-windows", str(_safe(path))], start_new_session=True)
    return f"Started Windows program {path} with Wine."

TOOLS = {
 "install_app": (t_install_app, "Install an app from the BharatOS store (Flathub), e.g. 'vscode', 'spotify', 'telegram', 'obs', 'zoom'.", {"name": "string"}, True),
 "run_windows_app": (t_run_windows_app, "Run a downloaded Windows .exe or .msi program.", {"path": "string"}, True),
 "open_app": (t_open_app, "Open a desktop application by name (files, browser, terminal, editor, settings, writer, calc, slides, music, photos, pdf, screenshot).", {"name": "string"}, False),
 "open_url": (t_open_url, "Open a website or Indian service (digilocker, umang, irctc, upi) in the browser.", {"url": "string"}, False),
 "web_search": (t_web_search, "Search the web in the browser.", {"query": "string"}, False),
 "list_files": (t_list_files, "List files in a folder (relative to home).", {"path": "string"}, False),
 "read_file": (t_read_file, "Read a text file.", {"path": "string"}, False),
 "write_file": (t_write_file, "Create or overwrite a text file, e.g. to build a website or app.", {"path": "string", "content": "string"}, True),
 "create_folder": (t_create_folder, "Create a folder.", {"path": "string"}, False),
 "move_file": (t_move_file, "Move or rename a file or folder.", {"src": "string", "dst": "string"}, True),
 "run_command": (t_run_command, "Run a shell command on this PC and return its output.", {"command": "string"}, True),
 "type_text": (t_type_text, "Type text into the focused window like a keyboard.", {"text": "string"}, True),
 "press_keys": (t_press_keys, "Press keys in the focused window, e.g. 'ctrl+s' or 'Return'.", {"keys": "string"}, True),
 "system_info": (t_system_info, "Get time, disk and memory info.", {}, False),
 "set_volume": (t_set_volume, "Set speaker volume percent.", {"percent": "integer"}, False),
}

def tool_schema():
    out = []
    for name, (_, desc, params, _) in TOOLS.items():
        out.append({"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": {k: {"type": v} for k, v in params.items()},
                           "required": list(params)}}})
    return out

SYSTEM = ("You are Companion, the built-in AI of BharatOS, an operating system made in India. "
          "You run fully offline on the user's PC and operate it for them using tools: open apps, "
          "browse, manage files, write code and websites, run commands. Plan briefly, use tools step by step, "
          "then reply in one or two short sentences. Reply in Hindi if the user writes in Hindi. "
          "Save new projects under ~/Documents. Never delete user data unless clearly asked.")

# ---------------------------------------------------------------- agent
class Agent(QtCore.QObject):
    step = QtCore.pyqtSignal(str)
    done = QtCore.pyqtSignal(str)
    confirm = QtCore.pyqtSignal(str, str)

    def __init__(self, cfg):
        super().__init__(); self.cfg = cfg; self.stop_flag = False
        self.history = [{"role": "system", "content": SYSTEM}]
        self._answer = None; self._ev = threading.Event()

    def answer_confirm(self, ok):
        self._answer = ok; self._ev.set()

    def run(self, text):
        self.stop_flag = False
        threading.Thread(target=self._loop, args=(text,), daemon=True).start()

    def _loop(self, text):
        self.history.append({"role": "user", "content": text})
        try:
            for _ in range(self.cfg["max_steps"]):
                if self.stop_flag:
                    return self.done.emit("Stopped. You're in control.")
                r = requests.post(self.cfg["ollama"] + "/api/chat", timeout=300, json={
                    "model": self.cfg["model"], "messages": self.history[-30:],
                    "tools": tool_schema(), "stream": False, "think": False})
                r.raise_for_status()
                msg = r.json()["message"]; self.history.append(msg)
                calls = msg.get("tool_calls") or []
                if not calls:
                    return self.done.emit(msg.get("content", "").strip() or "Done.")
                for c in calls:
                    name = c["function"]["name"]; args = c["function"].get("arguments") or {}
                    if isinstance(args, str):
                        args = json.loads(args or "{}")
                    fn, _, _, risky = TOOLS.get(name, (None, None, None, True))
                    if fn is None:
                        result = f"Unknown tool {name}."
                    else:
                        if risky and not self.cfg["autopilot"]:
                            self._ev.clear(); self.confirm.emit(name, json.dumps(args)[:300]); self._ev.wait()
                            if not self._answer:
                                result = "The user declined this step."
                                self.history.append({"role": "tool", "content": result, "tool_name": name}); continue
                        self.step.emit(f"{name.replace('_', ' ')}  {json.dumps(args)[:80]}")
                        try:
                            result = fn(**args)
                        except Exception as e:
                            result = f"Error: {e}"
                    self.history.append({"role": "tool", "content": str(result)[:6000], "tool_name": name})
            self.done.emit("I took the steps I could. Tell me what to do next.")
        except requests.ConnectionError:
            self.done.emit("My local AI isn't running yet. It finishes setting up on first boot once you're online.")
        except Exception as e:
            self.done.emit(f"Something went wrong: {e}")

# ---------------------------------------------------------------- UI
STYLE = """
QWidget#bar { background: rgba(31,31,31,235); border: 1px solid rgba(255,255,255,30); border-radius: 18px; }
QLineEdit { background: transparent; border: none; color: #F4F1EA; font-size: 20px; padding: 8px; }
QLabel { color: #F4F1EA; font-size: 13px; }
QLabel#hint { color: rgba(244,241,234,140); }
QPushButton { background: #C4622D; color: #F4F1EA; border: none; border-radius: 10px; padding: 6px 14px; font-size: 13px; }
QPushButton#ghost { background: rgba(255,255,255,20); }
"""

class Bar(QtWidgets.QWidget):
    def __init__(self, cfg):
        super().__init__(None, QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.Tool)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.cfg = cfg; self.agent = Agent(cfg)
        box = QtWidgets.QWidget(self); box.setObjectName("bar")
        lay = QtWidgets.QVBoxLayout(self); lay.addWidget(box)
        v = QtWidgets.QVBoxLayout(box); v.setContentsMargins(18, 14, 18, 14)
        top = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit(placeholderText="Tell Companion what you need…")
        self.auto = QtWidgets.QPushButton(); self.auto.setObjectName("ghost"); self.auto.clicked.connect(self.toggle_auto)
        self.stop = QtWidgets.QPushButton("Stop"); self.stop.clicked.connect(self.do_stop); self.stop.hide()
        top.addWidget(self.input, 1); top.addWidget(self.auto); top.addWidget(self.stop)
        self.log = QtWidgets.QLabel(""); self.log.setWordWrap(True)
        self.hint = QtWidgets.QLabel("Companion · " + cfg["model"] + " · runs on this PC   ·   Esc to close"); self.hint.setObjectName("hint")
        self.conf = QtWidgets.QWidget(); ch = QtWidgets.QHBoxLayout(self.conf); ch.setContentsMargins(0, 0, 0, 0)
        self.conf_lbl = QtWidgets.QLabel(); yes = QtWidgets.QPushButton("Allow"); no = QtWidgets.QPushButton("Skip"); no.setObjectName("ghost")
        yes.clicked.connect(lambda: self.answer(True)); no.clicked.connect(lambda: self.answer(False))
        ch.addWidget(self.conf_lbl, 1); ch.addWidget(yes); ch.addWidget(no); self.conf.hide()
        for w in (self.log, self.conf, self.hint): v.addWidget(w)
        v.insertLayout(0, top)
        self.setStyleSheet(STYLE); self.resize(720, 150); self.refresh_auto()
        self.input.returnPressed.connect(self.submit)
        self.agent.step.connect(lambda s: self.log.setText("Working · " + s))
        self.agent.done.connect(self.finished); self.agent.confirm.connect(self.ask)

    def refresh_auto(self):
        self.auto.setText("Autopilot: On" if self.cfg["autopilot"] else "Ask me first")

    def toggle_auto(self):
        self.cfg["autopilot"] = not self.cfg["autopilot"]; save_cfg(self.cfg); self.refresh_auto()

    def submit(self):
        t = self.input.text().strip()
        if not t: return
        self.input.clear(); self.log.setText("Thinking…"); self.stop.show(); self.agent.run(t)

    def ask(self, name, args):
        self.conf_lbl.setText(f"Allow: {name.replace('_', ' ')} {args}?"); self.conf.show()

    def answer(self, ok):
        self.conf.hide(); self.agent.answer_confirm(ok)

    def do_stop(self):
        self.agent.stop_flag = True; self.answer(False)

    def finished(self, text):
        self.stop.hide(); self.log.setText(text)

    def toggle(self):
        if self.isVisible(): self.hide(); return
        g = QtGui.QGuiApplication.primaryScreen().geometry()
        self.move(g.center().x() - self.width() // 2, int(g.height() * 0.18))
        self.show(); self.raise_(); self.activateWindow(); self.input.setFocus()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key.Key_Escape:
            if self.stop.isVisible(): self.do_stop()
            else: self.hide()

def main():
    app = QtWidgets.QApplication(sys.argv); app.setQuitOnLastWindowClosed(False)
    sock = QtNetwork.QLocalSocket(); sock.connectToServer(APP_ID)
    if sock.waitForConnected(300):
        sock.write(b"toggle"); sock.flush(); sock.waitForBytesWritten(300); return
    QtNetwork.QLocalServer.removeServer(APP_ID)
    server = QtNetwork.QLocalServer(); server.listen(APP_ID)
    bar = Bar(load_cfg())
    server.newConnection.connect(lambda: (server.nextPendingConnection(), bar.toggle()))
    tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon.fromTheme("bharatos-companion", QtGui.QIcon.fromTheme("help-about")))
    m = QtWidgets.QMenu(); m.addAction("Open Companion", bar.toggle); m.addAction("Quit", app.quit)
    tray.setContextMenu(m); tray.activated.connect(lambda *_: bar.toggle()); tray.setToolTip("Companion AI"); tray.show()
    if "--background" not in sys.argv: bar.toggle()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
