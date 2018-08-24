from PySide2 import QtCore
import subprocess
import re
import types
import json


# executes the given command and returns the result
def _exec_to_str(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, _ = proc.communicate()
    proc.wait()
    return out.decode('utf-8')


# gets the currently active window title
def active_window_title():
    return _exec_to_str('xdotool getactivewindow getwindowname')


# gets the currently active window id
def active_window_id():
    return int(_exec_to_str('xdotool getactivewindow'))


# moves the window with the given id to the given coordinates
def move_window(wid, x, y):
    return _exec_to_str('xdotool windowmove %s %s %s' % (wid, x, y))


# resizes the window with the given id to the given dimensions
def size_window(wid, w, h):
    return _exec_to_str('xdotool windowsize %s %s %s' % (wid, w, h))


# sets the window with the given id to the given bounds
def set_window_bounds(wid, x, y, w, h):
    return _exec_to_str('wmctrl -i -r %s -e 0,%s,%s,%s,%s' % (wid, x, y, w, h))


# converts the getwindowgeometry command output to a singleton
def parse_window_geometry(output):
    pos = re.search('([0-9]+),([0-9]+)', output)
    geom = re.search('([0-9]+)x([0-9]+)', output)
    x, y = int(pos.group(1)), int(pos.group(2))
    w, h = int(geom.group(1)), int(geom.group(2))
    return types.SimpleNamespace(x=x, y=y, w=w, h=h)


# gets the geometry of the window with the given id
def window_region(wid):
    return parse_window_geometry(_exec_to_str('xdotool getwindowgeometry %s' % (wid)))


# gets the currently active window's geometry
def active_window_region():
    return window_region(active_window_id())


def window_classes(wid):
    out = _exec_to_str('xprop -id %s WM_CLASS' % (wid))
    right = out[(out.index(' = ') + 3):]
    classes = right.split(',')
    for x in range(0, len(classes)):
        classes[x] = classes[x].strip().replace('"', '')
    return classes


# gets the list of currently opened windows
def window_list():
    out = _exec_to_str('wmctrl -l | awk \'{$3=""; $2=""; print $0}\'')
    out_data = out.strip().split('\n')
    win_data = []
    for data in out_data:
        spaceIdx = data.index(' ')
        wid = int(data[0:spaceIdx], 0)
        title = data[spaceIdx:].strip()
        geom = window_region(wid)
        wclass = window_classes(wid)[-1]
        win_data.append(types.SimpleNamespace(
            wid=wid, title=title, bounds=geom, wclass=wclass))
    return win_data


# counts the amount of screens the given rectangle intersects
def intersect_count(screens, rect):
    count = 0
    for screen in screens:
        if rect.intersects(screen.availableGeometry()):
            count += 1
    return count


# organizes the window listing into each monitor number index in an array
def screen_window_list(app):
    windows = window_list()
    screens = app.screens()
    win_list = [None] * len(screens)
    for x in range(0, len(screens)):
        win_list[x] = []
        region = screens[x].availableGeometry()
        for window in windows:
            win_region = window.bounds
            win_rect = QtCore.QRect(
                win_region.x, win_region.y, win_region.w, win_region.h)
            if intersect_count(screens, win_rect) == 1 and win_rect.intersects(region):
                win_list[x].append(window)
    return win_list


# converts the given window list into a json configuration
def create_config(app, win_list):
    obj = {
        'x_off': '0',
        'y_off': '0',
        'screens': {}
    }
    screens = app.screens()
    for i in range(0, len(win_list)):
        region = screens[i].geometry()
        top = region.topLeft()
        screen_list = []
        for win in win_list[i]:
            entry = {
                'wclass': win.wclass,
                'x': '%s' % (win.bounds.x - top.x()),
                'y': '%s' % (win.bounds.y - top.y()),
                'w': '%s' % (win.bounds.w),
                'h': '%s' % (win.bounds.h)
            }
            screen_list.append(entry)
        obj['screens'][i] = screen_list
    return obj


# writes the current config to the given json file
def write_current_config(app, path):
    win_list = screen_window_list(app)
    config = create_config(app, win_list)
    with open(path, 'w') as outfile:
        json.dump(config, outfile, indent=2)


# gets the amount of occurences of the given wclass
def count_wclass(win_list, wclass):
    count = 0
    for win in win_list:
        if win.wclass == wclass:
            count += 1
    return count


# finds a window in the window list with the given wclass
def find_win(win_list, wclass):
    for win in win_list:
        if win.wclass == wclass:
            return win
    raise Exception('no window wclass=%s exists' % (wclass))


# sets the window to the bounds of the given config
def set_win_cfg_bounds(region, win_cfg, win):
    top = region.topLeft()
    x = (int(win_cfg['x']) + top.x())
    y = (int(win_cfg['y']) + top.y())
    # size down the window first for correct moving/sizing
    size_window(win.wid, 100, 100)
    move_window(win.wid, x, y)
    size_window(win.wid, win_cfg['w'], win_cfg['h'])


# applies the configuration of the given file
def apply_config(app, path):
    win_list = window_list()
    screens = app.screens()
    visited = []
    multiples = []
    with open(path, 'r') as infile:
        config = json.load(infile)
        off_x = int(config['off_x']) if 'off_x' in config else 0
        off_y = int(config['off_y']) if 'off_y' in config else 0
        print(off_x, off_y)
        for i in range(0, len(config['screens'])):
            screen = config['screens'][str(i)]
            region = screens[i].geometry()
            for window in screen:
                window['x'] = (int(window['x']) + off_x)
                window['y'] = (int(window['y']) + off_y)
                wc = window['wclass']
                if wc not in visited:
                    visited.append(wc)
                    if count_wclass(win_list, wc) == 1:
                        match = find_win(win_list, wc)
                        set_win_cfg_bounds(region, window, match)
                    else:
                        multiples.append(wc)
