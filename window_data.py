import subprocess
import re
import types


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


# gets the currently active window's geometry
def active_window_region():
    out = _exec_to_str('xdotool getactivewindow getwindowgeometry')
    pos = re.search('([0-9]+),([0-9]+)', out)
    geom = re.search('([0-9]+)x([0-9]+)', out)
    x, y = int(pos.group(1)), int(pos.group(2))
    w, h = int(geom.group(1)), int(geom.group(2))
    return types.SimpleNamespace(x=x, y=y, w=w, h=h)