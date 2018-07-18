# Radio Paradise player and notifier

Radio paradise: https://www.radioparadise.com

This program plays radio paradise's stream from cli and send notifications on what's currently playing using your desktop notification system.

This is tested (and certainly working only) under linux.

## usage

* Launch the program in command line with

```$ paradise_player```

* or the shortcut

```$ rpp```

* it will start to play the steam and send notification when song changes.


* Ctrl+C to stop it

## installation

```$ pip install paradise_player```

or clone the repository [from github](https://github.com/ThomasChiroux/paradise_player) and run

```$ python setup.py install```

## configuration

config file is stored in ~/.config/paradise_player/config.cfg

see file config_sample.cfg for all configuration parameters.

## dependencies

* This program requires notify-send on your system.

For archlinux, install libnotify:

```$ sudo pacman -S libnotify```

* It also requires a notification server, generally built-in if you use 'big' desktop environments like gnome or kde.

Alternatively, you can use dunst (https://dunst-project.org/)

* playing the radio stream is configurable, vlc is used by default.
  you can use ffplay (from ffmpeg), mplayer, or any cli player capable of playing http streams.

* of course this program requires python 3+ installed in your system.

## credits

Inspired by https://github.com/jmdh/rpnotify/blob/master/rpnotify
