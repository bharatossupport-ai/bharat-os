# BharatOS

**An AI-operated operating system, made in India.** BharatOS is a Debian-based Linux distribution with a built-in offline AI, **Companion**, that can operate your PC for you: open apps, browse, manage files, write code and build websites. You stay in control with *Ask me first*, *Autopilot*, and *Stop*.

## What's inside (v1.0 "Ganga")
- **Base:** Debian 13 (trixie), 64-bit, KDE Plasma desktop
- **Companion AI:** press **Meta + Space** anywhere. Runs locally through Ollama on **Qwen3.5 4B** (~3.4 GB RAM, works on 6 GB PCs). Tools: open apps, open websites and Indian services (DigiLocker, UMANG, IRCTC, UPI), web search, read/write files, create folders, run commands, type and press keys, volume, system info.
- **First-run tour:** language, meet Companion, try a command, Autopilot vs Ask me first.
- **Made for India:** Indic fonts and input (ibus-m17n), en_IN/hi_IN locales, IST time zone.
- **Windows apps:** double-click any `.exe` or `.msi` to run it (Wine 10, 64- and 32-bit). Many apps work; heavy games and anti-cheat software may not.
- **App Store:** Discover with Flathub: VS Code, Spotify, Telegram, OBS, Zoom, Steam, Chrome and thousands more. Or ask Companion: "install spotify".
- **Mac files:** `.dmg` and `.pkg` open and show their files; Mac drives (HFS+) can be read. Mac programs themselves cannot run on a PC, so BharatOS points you to the Linux or Windows version.
- **Installer:** Calamares (graphical), branded BharatOS.
- **Look:** dark charcoal with terracotta accent, Himalaya wallpaper.

## Mac and Windows features, BharatOS style
| You know it as | In BharatOS | Shortcut |
|---|---|---|
| Spotlight / Windows Search | Search (KRunner) | Alt+Space |
| Siri / Copilot | Companion AI (offline) | Meta+Space |
| Dock / Taskbar | Centred floating dock | |
| Start menu / Launchpad | App Drawer (top-left) | Meta |
| Mission Control / Task View | Overview, 4 desktops, hot corner top-left | Meta+W |
| Snap Layouts / Split View | Window tiling | Meta+T, Meta+arrows |
| Clipboard history | Clipboard | Meta+V |
| Snipping Tool / Screenshot | Spectacle | Meta+Shift+S |
| File Explorer / Finder (with Quick Look previews) | Files (Dolphin) | Meta+E |
| Task Manager / Activity Monitor | System Monitor | Ctrl+Shift+Esc |
| Settings / System Settings | Settings | Meta+I |
| Phone Link / AirDrop / Continuity | KDE Connect (Android and iPhone) | |
| Time Machine / File History | Timeshift backups | |
| FileVault / BitLocker | Full-disk encryption in installer, Vault folders | |
| Windows Defender Firewall | Firewall (on by default) | |
| Keychain / Credential Manager | Wallet | |
| Disk Utility | Partition Manager, Disk health, Filelight | |
| Remote Desktop | KRDC / Desktop Sharing | |
| Night Shift / Night light | Night Colour (automatic) | |
| App Store / Microsoft Store | Discover + Flathub | |
| Calculator, Clock, Calendar, Camera, Music, Video, Office | KCalc, Clock, Merkuro, Kamoso, Elisa, Haruna, LibreOffice | |
| Run Windows apps | Wine (double-click .exe/.msi) | |

Not possible on any PC Linux: running macOS apps, iCloud/iMessage, Xbox Game Pass, and games with kernel anti-cheat.

## Get the ISO
1. Open the **Actions** tab → **Build BharatOS ISO** → **Run workflow** (or push to `main`).
2. When the run finishes (about 30–60 min), download the **BharatOS-1.0-amd64** artifact.
3. Flash it to a USB stick with [balenaEtcher](https://etcher.balena.io/) or Rufus (DD mode), or boot it in VirtualBox/QEMU.
4. Try it live, then click **Install** to put it on your PC.

On first boot of the *installed* system with internet, BharatOS downloads Ollama and the Companion model (~3 GB) in the background. After that, Companion works fully offline.

## Build locally (Debian/Ubuntu host)
```bash
sudo apt install live-build
sudo lb config && sudo lb build
```

## Repo layout
- `auto/` – live-build configuration
- `config/package-lists/` – packages (desktop, India, Companion)
- `config/hooks/live/` – branding, locales, wallpaper, installer branding
- `config/includes.chroot/` – files copied into the OS (Companion AI, tour, settings)

## Roadmap
- BharatOS shell: Dynamic Island, App Drawer, dock (custom Plasma theme)
- Companion: screen reading with vision, voice input, Hindi replies
- Optional bigger model on 16 GB PCs (Qwen3.5 9B)
- Model bundled in the ISO for fully offline installs
