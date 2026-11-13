#!/usr/bin/env python3
"""First-run tour for BharatOS: language, meet Companion, try it, stay in control."""
import json, pathlib, subprocess, sys
from PyQt6 import QtCore, QtWidgets

DONE = pathlib.Path.home() / ".config" / "bharatos" / "welcome-done"
CFG = pathlib.Path.home() / ".config" / "bharatos" / "companion.json"
STEPS = [
 ("Welcome to BharatOS", "Made in India, for you. Choose your language to begin.", "lang"),
 ("Meet Companion", "Companion is the AI built into BharatOS. It runs on this PC, works offline, and can open apps, browse, organise files and even build websites for you.", None),
 ("Try it", "Press Meta + Space (the Windows key and Space) anywhere, then type: open files", "try"),
 ("You stay in control", "Companion asks before risky steps. Switch to Autopilot when you trust it. Press Esc or Stop at any time to take over.", "auto"),
 ("Your local AI", "On first boot with internet, BharatOS downloads Companion's brain (Qwen3.5 4B, about 3 GB). After that it works fully offline.", None),
 ("You're ready", "Enjoy BharatOS. You can replay this tour from the app menu: Welcome to BharatOS.", None),
]
QSS = """QWidget{background:#1F1F1F;color:#F4F1EA;font-size:15px}
QLabel#t{font-size:28px;font-weight:600}
QPushButton{background:#C4622D;border:none;border-radius:10px;padding:8px 18px}
QPushButton#g{background:#333}
QComboBox{background:#2A2A2A;border:1px solid #444;border-radius:8px;padding:6px}"""

class Tour(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.i = 0; self.setWindowTitle("Welcome to BharatOS"); self.resize(620, 360)
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(36, 32, 36, 28)
        self.dots = QtWidgets.QLabel(); self.t = QtWidgets.QLabel(objectName="t"); self.b = QtWidgets.QLabel(wordWrap=True)
        self.extra = QtWidgets.QStackedWidget()
        self.lang = QtWidgets.QComboBox(); self.lang.addItems(["English", "हिन्दी", "বাংলা", "தமிழ்", "తెలుగు", "मराठी", "ગુજરાતી", "ಕನ್ನಡ", "മലയാളം", "ਪੰਜਾਬੀ", "ଓଡ଼ିଆ"])
        tryb = QtWidgets.QPushButton("Open Companion now"); tryb.clicked.connect(lambda: subprocess.Popen(["companion"]))
        self.autob = QtWidgets.QCheckBox("Turn on Autopilot (Companion acts without asking)")
        for w in (QtWidgets.QWidget(), self.lang, tryb, self.autob): self.extra.addWidget(w)
        nav = QtWidgets.QHBoxLayout(); self.back = QtWidgets.QPushButton("Back", objectName="g"); skip = QtWidgets.QPushButton("Skip", objectName="g")
        self.next = QtWidgets.QPushButton("Next"); nav.addWidget(skip); nav.addStretch(); nav.addWidget(self.back); nav.addWidget(self.next)
        self.back.clicked.connect(lambda: self.go(-1)); self.next.clicked.connect(lambda: self.go(1)); skip.clicked.connect(self.finish)
        for w in (self.dots, self.t, self.b, self.extra): v.addWidget(w)
        v.addStretch(); v.addLayout(nav); self.setStyleSheet(QSS); self.render()

    def render(self):
        t, b, k = STEPS[self.i]
        self.dots.setText("  ".join("●" if j == self.i else "○" for j in range(len(STEPS))))
        self.t.setText(t); self.b.setText(b)
        self.extra.setCurrentIndex({None: 0, "lang": 1, "try": 2, "auto": 3}[k])
        self.back.setEnabled(self.i > 0); self.next.setText("Start using BharatOS" if self.i == len(STEPS) - 1 else "Next")

    def go(self, d):
        if self.i + d >= len(STEPS): return self.finish()
        self.i = max(0, self.i + d); self.render()

    def finish(self):
        DONE.parent.mkdir(parents=True, exist_ok=True); DONE.touch()
        try: cfg = json.loads(CFG.read_text())
        except Exception: cfg = {}
        cfg["autopilot"] = self.autob.isChecked(); cfg["language"] = "hi" if self.lang.currentIndex() == 1 else "en"
        CFG.write_text(json.dumps(cfg, indent=2)); self.close()

if __name__ == "__main__":
    if DONE.exists() and "--force" not in sys.argv: sys.exit(0)
    app = QtWidgets.QApplication(sys.argv); w = Tour(); w.show(); sys.exit(app.exec())
