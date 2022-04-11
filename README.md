# README

## Installation

Prerequisites: Python 3.x, pip
Place PaintMixer-qt5 directory in home directory
Install by running:

```
sudo sh ./install.sh
```

## Usage

Start PaintMixer.sh (here on on desktop)
or run

```
python MainView.py
```

## Changelog
### v1.1 - 30 mar 2022
Added support for telling the controller about colors saved in config file. After changing a color in ‘Edit’ settings it’s code is also told to the controller.
Every click on GUI element invokes sending ‘ \r\n’ to the controller
