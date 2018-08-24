# GridWM

This program aims to make it easy to have a clean workspace with easy to make user-profiles and quick shortcuts to move windows around.

![](https://img.shields.io/badge/License-MIT-blue.svg)


![](md_res/showcase.gif)


## Installation

### Linux/OS X

```
sudo git clone https://github.com/TSedlar/GridWM.git /usr/local/src/gridwm
cd /usr/local/src/gridwm
./install.sh
```

### Windows

Windows is not currently supported but will be soon.


## Standard running

Map the `gridwm` command to a key combination to run it on the currently active window.


## Profiles
Clicking the export button will result in the ability to create a JSON configuration.

These are saved under ~/.gridwm/<given_name>.json

It will set the dimensions of every program listed in the configuration that is opened.

It's suggested to map the below command to a key combination to automatically set your layout upon the keys being pressed.

```
gridwm --config=~/.gridwm/<given_name>.json
```

TODO: fix location setting for duplicates (i.e 2 firefox windows)

## Linux/OS X Requirements

These should be already installed by default, except possibly xdotool:
- xdotool
- wmctrl
- awk
- xprop
- cat

## Windows Requirements

Windows is not currently supported but will be soon.