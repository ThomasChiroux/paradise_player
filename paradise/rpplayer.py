#!/usr/bin/env python
"""Small script to send notifications for song change in Radio paradise.

config is stored in ~/.config/paradise_player/config.cfg

System requirements:
* notify-send
* ffplay or vlc or mplayer...
"""
import configparser
import logging
import os
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET

# for debugging purposes:
from pprint import pprint

import requests
from requests.exceptions import RequestException


def get_image(url, tmpdir):
    """get an image from url, store it in temp file and return the filename."""
    if url is not None:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(tmpdir, uuid.uuid4().hex + ".jpg")
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename


def notify(notify_cmd, title, content, image=None, urgency='normal'):
    """notify a user using notify_cmd."""
    cmd = notify_cmd.format(urgency=urgency).split(" ")
    if image:
        cmd.append("-i")
        cmd.append(image)
    cmd.append(title)
    cmd.append(content)
    subprocess.call(cmd)
    logging.debug(cmd)
    # print currently playing in stdout
    if urgency == 'normal':
        print(title.replace("\n", " ") + " - " + content.replace("\n", " "))


def play_stream(cmd):
    """Play the radio paradise stream using FFPLAY command."""
    cmd = cmd.split(" ")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc


def format_string(string, data):
    """Format a string for notification, based on all content data."""
    return string.format(
        refresh_time=data.get("refresh_time", ""),
        playtime=data.get("playtime", ""),
        timestamp=data.get("timestamp", ""),
        artist=data.get("artist", ""),
        title=data.get("title", ""),
        songid=data.get("songid", ""),
        album=data.get("album", ""),
        asin=data.get("asin", ""),
        rating=data.get("rating", ""),
        coverart=data.get("coverart", ""),
        release_date=data.get("release_date", ""))
        

def play(config):
    """Play the steam and get last song in RP xml stream and send notify.

    Data Content is (with sample):
    
    refresh_time: 1531326250
    playtime:  9:17 am
    timestamp:  1531325859
    artist:  Sinéad O'Connor
    title:  You Made Me The Thief Of Your Heart
    songid:  32497
    album:  In The Name of the Father OST
    asin:  B000001E2H
    rating:  7.51
    coverart:  https://img.radioparadise.com/covers/l/B000001E2H.jpg
    release_date:  1994
    """
    next_refresh = time.time()
    last_refresh = time.time() - config.getint("system", "default_refresh") - 1
    middle_refresh = None
    last_image = None
    last_song = None
    current_song = None

    # start the stream
    print("Playing radio paradise...")
    proc = play_stream(
        config.get("player", "play_cmd").format(url=config.get('stream', "url")))

    # monitor the stream and get info about what is steamed for notify
    try:
        while True:
            # monitor the stream
            try:
                out, err = proc.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            else:
                if err is not None:
                    logging.error("STREAM PLAYER ERROR: %s", err)
            # refresh datas
            if (time.time() >= next_refresh and 
                    time.time() >= last_refresh + config.getint("system", 
                                                                "default_refresh")):
                logging.debug(str(time.time()) + ": request...")
                resp = requests.get(config.get('stream', "data"))
                try:
                    resp.raise_for_status()
                except RequestException:
                    pass
                else:
                    root = ET.fromstring(resp.content)
                    current_song = {}
                    for child in root:
                        current = child
                        break
                    for elt in current:
                        current_song[elt.tag] = elt.text
                    # now I have a dict with current_song datas
                    # some debug:
                    # print("=== %s: " % time.time())
                    # pprint(current_song)
                    # end of debug
                    if current_song.get('songid') != last_song:
                        # yes the song has changed: display a new notification:
                        
                        image = get_image(current_song.get('coverart'),
                                          tmpdir=config.get("system", "tmpdir"))
                        notify(
                            config.get('notification', 'notify_cmd'),
                            format_string(config.get('notification', 'title'), 
                                          current_song),
                            format_string(config.get('notification', 'content'), 
                                          current_song),
                            image=image)
                        if last_image:
                            try:
                                os.remove(last_image)
                            except FileNotFoundError:
                                pass
                        last_image = image
                        last_song = current_song.get('songid')
                        last_refresh = time.time()
                        next_refresh = int(current_song.get(
                            'refresh_time', 
                            time.time())) + config.getint("system", "offset")
                        middle_refresh = int(last_refresh + 
                                             (next_refresh - last_refresh) / 2)
                    else:  
                        # we refreshed, but got the same song.. this is kind of wrong
                        # TODO: do something to 'learn' the offset and use it later
                        # print("== Debug: Last refresh too soon")
                        last_refresh = time.time()
                        next_refresh = int(current_song.get(
                            'refresh_time', 
                            time.time())) + config.getint("system", "default_refresh")
                    
            elif (config.getboolean("notification", "repeat_notification") and
                    middle_refresh is not None and 
                    time.time() >= middle_refresh and current_song is not None):
                # repeat notification in the middle of the song in low level
                notify(
                    config.get('notification', 'notify_cmd'),
                    format_string(config.get('notification', 'repeat_title'), 
                                  current_song),
                    format_string(config.get('notification', 'repeat_content'), 
                                  current_song),
                    image=last_image,
                    urgency='low')
                middle_refresh = None
            time.sleep(1)
    except (KeyboardInterrupt, Exception) as exc:
        logging.error("Exception: %s (%s), stop..." % (exc.__class__.__name__, exc))
        try:
            proc.kill()
        except Exception:
            pass
        if last_image:
            try:
                os.remove(last_image)
            except FileNotFoundError:
                pass


def main():
    """Read the config and start playing."""
    logging.basicConfig()
    config = configparser.SafeConfigParser()
    config['DEFAULT'] = {
        "url": "http://stream-uk1.radioparadise.com/aac-320",
        "data": "http://www.radioparadise.com/chumby.xml",
        "notify_cmd": 'notify-send -u {urgency} -a "radio_paradise"',
        "repeat_notification": True,
        "title": "{artist}",
        "content": "{title}\n[{album} - {release_date}]",
        "repeat_title": "{artist}",
        "repeat_content": "{title}\n[{album} - {release_date}]\n"
                          "<small><i>(currently playing)</i></small>",
        "play_cmd": "cvlc --http-reconnect --repeat {url}",
        "default_refresh": "30",
        "offset": "62",
        "tmpdir": "/tmp/",
    }
    config.read(os.path.expanduser('~/.config/paradise_player/config.cfg'))
    play(config)


if __name__ == '__main__':
    main()