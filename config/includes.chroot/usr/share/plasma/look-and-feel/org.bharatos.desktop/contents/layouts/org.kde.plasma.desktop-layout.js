// BharatOS default desktop: slim top bar (App Drawer left, island clock centre, tray right) + centred floating dock

// Desktop wallpaper
var desktops = desktopsForActivity(currentActivity());
for (var i = 0; i < desktops.length; i++) {
    var d = desktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/BharatOS/contents/images/2400x1600.jpg");
    d.writeConfig("FillMode", "2");
}

// Top bar
var top = new Panel;
top.location = "top";
top.height = Math.round(gridUnit * 1.6);
top.floating = false;
var drawer = top.addWidget("org.kde.plasma.kickoff");
drawer.currentConfigGroup = ["General"];
drawer.writeConfig("icon", "start-here");
drawer.writeConfig("favoritesDisplay", "0");
top.addWidget("org.kde.plasma.appmenu");
top.addWidget("org.kde.plasma.panelspacer");
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd d MMM");
clock.writeConfig("use24hFormat", "0");
top.addWidget("org.kde.plasma.panelspacer");
top.addWidget("org.kde.plasma.systemtray");

// Dock
var dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(gridUnit * 3.2);
dock.alignment = "center";
dock.lengthMode = "fit";
dock.floating = true;
dock.hiding = "dodgewindows";
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
  "applications:systemsettings.desktop",
  "applications:org.kde.dolphin.desktop",
  "applications:firefox-esr.desktop",
  "applications:bharatos-companion.desktop",
  "applications:org.kde.kate.desktop",
  "applications:libreoffice-writer.desktop",
  "applications:org.kde.elisa.desktop",
  "applications:org.kde.discover.desktop",
  "applications:org.kde.konsole.desktop"
].join(","));
tasks.writeConfig("showOnlyCurrentDesktop", "false");
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");
