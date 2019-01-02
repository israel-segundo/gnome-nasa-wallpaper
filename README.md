# gnome-nasa-wallpaper
Linux application for GNOME and Python3 for setting up a dynamic wallpaper using NASA's "Astronomy Picture of the Day" and a menu on the taskbar for reading information about the image.


# Requirements
- Python 3 or greater.
- Needs internet access at startup.
- Read/Write permissions on /tmp volume.
- The following python packages:
-- requests==2.18.4

# How to add at startup

1. Open 'Startup Applications'
2. Click 'Add'
3. Command should be 'python nasa_random_wallpaper_gnome.py &'. 
4. (optional) Click 'Run now'

# Screenshots

## Icon on taskbar (GTK's StatusIcon)
![Alt text](/../master/img/applet_icon.png?raw=true "Icon on taskbar")
![Alt text](/../master/img/context_menu.png?raw=true "Context Menu")

## When right-clicking the icon, the default browser will open the NASA webpage of the image.
![Alt text](/../master/img/click_open_webbrowser.png?raw=true "Open webbrowser")
