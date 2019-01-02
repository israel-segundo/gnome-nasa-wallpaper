"""

    Author: israel-segundo

    This small application will spawn a process that retrieves a random image from 
    NASA and will use it as wallpaper of a GNOME system. 
    
    The application maintains a status icon in the task bar and some information about
    the image can be seen by clicking the icon.


    NASA API Documentation: 
    https://open.nasa.gov/blog/explore-brand-new-updates-astronomy-picture-day-apod-api/

    Change GNOME Wallpaper code snippet extracted from:
    https://askubuntu.com/questions/85162/how-can-i-change-the-wallpaper-using-a-python-script/85191
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from gi.repository import Notify as notify

from datetime import datetime  
import os
import signal
import requests
import urlparse
import logging
import logging.config
import webbrowser

logger = logging.getLogger(__name__)

class NasaStatusIcon:

    APP_ID           = 'nasabackgroundstatusicon'
    ICON_FILE_NAME   = 'nasa-logo.svg'
    APP_TOOLTIP_TEXT = 'Daily Nasa Background Image'

    def __init__(self):

        self.nasacrawler = NasaImageCrawler()
        self.status_icon = gtk.StatusIcon()

        self.status_icon.set_from_file(os.path.abspath(self.ICON_FILE_NAME))
        self.status_icon.set_tooltip_text(self.APP_TOOLTIP_TEXT)        
        self.status_icon.connect("activate", self.show_image_data)
        self.status_icon.connect("popup-menu", self.right_click_event)
        
        notify.init(self.APP_ID)

        
    def show_image_data(self, source):
        logger.info("Opening browser using URL: " + self.nasacrawler.get_image_url())
        webbrowser.open_new_tab(self.nasacrawler.get_image_url())
    
    def right_click_event(self, icon, button, time):
        self.menu = gtk.Menu()

        # About Image Button
        item_balloon = gtk.MenuItem('About Image')
        item_balloon.connect('activate', self.nasacrawler.about_image)
        self.menu.append(item_balloon)

        # Refress image button
        refresh_image_btn = gtk.MenuItem('Refresh Image')
        refresh_image_btn.connect('activate', self.refresh_image)
        self.menu.append(refresh_image_btn)

        # Separator
        self.menu.append(gtk.SeparatorMenuItem())

        # Quit button
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        self.menu.append(item_quit)                

        self.menu.show_all()
        self.menu.popup(None, None, None, self.status_icon, button, time)
    
    def refresh_image(self, source):
        self.nasacrawler = NasaImageCrawler()

    def quit(self, source):
        notify.uninit()
        gtk.main_quit()

class NasaImageCrawler:

    NASA_API_APOD_URL = "https://api.nasa.gov/planetary/apod"
    NASA_APOD_URL     = "https://apod.nasa.gov/apod/apYYMMDD.html"

    NASA_API_PARAMS   = {
        'api_key': 'DEMO_KEY',
        'count': '1'
    }

    def __init__(self):
        self.crawl_image()

        if self.apod:

            self.download_image_to_tmp()
            self.set_wallpaper()
    
    def get_image_url(self):
        return self.apod['apod_url']

    def download_image_to_tmp(self):
        
        if 'hdurl' in self.apod:
            url   = self.apod['hdurl']
        else:
            url   = self.apod['url']

        fpath = urlparse.urlparse(url) 
        image_name = os.path.basename(fpath.path)
        disk_path  = '/tmp/' + image_name

        logger.info("Downloading image {0} from {1}".format(image_name, url))
        
        req_img = requests.get(url)

        logger.info(req_img.status_code)

        if req_img.ok:
            logger.info("Download successful. Saving to disk on {0}".format(disk_path))
            f = open(disk_path,'wb')
            f.write(req_img.content)
            f.close()

            self.apod['image_disk_url'] = "file:///tmp/" + image_name
            self.apod['image_path'] = disk_path

            date_object = datetime.strptime(self.apod['date'], '%Y-%m-%d')  
            fdate       = date_object.strftime('%y%m%d')
            self.apod['apod_url'] = self.NASA_APOD_URL.replace('YYMMDD', fdate)

            logger.info(self.apod['apod_url'])


    def set_wallpaper(self):
        
        if self.apod:
            logger.info('Setting wallpaper to use image: {0}'.format(self.apod['image_path']))
            logger.info('picture-uri: {0}'.format(self.apod['image_disk_url']))

            schema = 'org.gnome.desktop.background'
            key    = 'picture-uri'

            gsettings = gio.Settings.new(schema)
            gsettings.set_string(key, self.apod['image_disk_url'])

    def crawl_image(self):

        r = requests.get(self.NASA_API_APOD_URL, params=self.NASA_API_PARAMS)
        if r.ok and len(r.json()) > 0:
            self.apod = r.json()[0]
            logger.info(self.apod)
        else:
            logger.error("Failed request to NASA")

    def about_image(self,_):

        if self.apod:

            summary = "{title}. \nTaken in {date}".format(title=self.apod['title'], \
                                                        date=self.apod['date'])

            notification = notify.Notification.new(summary, \
                                                   self.apod['explanation'], \
                                                   None)
            notification.show()

        else:
            logger.error("No apod available")

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = NasaStatusIcon()
    gtk.main()

if __name__ == "__main__":
    logging.basicConfig(filename='/tmp/nasawallpaper.log', \
                        filemode='w', \
                        format='%(name)s - %(levelname)s - %(message)s', \
                        level=logging.DEBUG)    
    main()