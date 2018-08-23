from PySide2 import QtWidgets, QtGui, QtCore
import window_data as WinData
import time
import types


BLOCKS = 20
MARGIN = 20
GRID_COLOR = QtGui.QColor(80, 80, 80)
GRID_BG_COLOR = QtGui.QColor(40, 40, 40)
FRAME_COLOR = QtGui.QColor(120, 120, 120)
REGION_COLOR = QtGui.QColor(15, 15, 15)


# gets the currently active monitor screen
def active_screen(app):
    return app.screens()[app.desktop().screenNumber(QtGui.QCursor.pos())]


# gets the currently active monitor screen geometry
def active_screen_region(app):
    return active_screen(app).availableGeometry()

# moves the given window on the given monitor with the window id to the bounds
def change_window_region(active_region, wid, bounds):
    top = active_region.topLeft()
    tx = int(top.x() + bounds.x() + (MARGIN / 2.0))
    ty = int(bounds.y() + (MARGIN / 2.0)) + top.y()
    tw = (bounds.width() - MARGIN)
    th = (bounds.height() - MARGIN) - top.y()
    neg = (MARGIN / (BLOCKS / 4.0))
    distFromLeft = abs(tx - top.x())
    distFromRight = abs((tx + tw) - (top.x() + active_region.width()))
    distFromTop = abs(ty - top.y())
    distFromBot = abs((ty + th) - (active_region.height()))
    if distFromLeft < MARGIN:
        tx += neg
    if distFromRight < MARGIN:
        tx -= neg
    if distFromTop < MARGIN:
        ty += neg
    if distFromBot < MARGIN:
        ty -= neg
    WinData.size_window(wid, 0, 0) # size down the window first for correct moving/sizing
    WinData.move_window(wid, tx, ty)
    WinData.size_window(wid, tw, th)


# creates a grid with a callback system on the given widget
def do_grid(grid, callback):
    # create grid data
    size = int(grid.width() / BLOCKS)
    # loop through the grid
    for x in range(0, BLOCKS):
        for y in range(0, BLOCKS):
            callback(QtCore.QRect(x * size, y * size, size, size))


# moves the window with the given id to the region specified
def size_and_hide(window, grid, active_region, wid, region):
    # create the snapped region
    snapped = QtCore.QRect(-1, -1, -1, -1)
    def grid_callback(rect):
        if rect.intersects(region):
            if snapped.x() == -1 or snapped.y() == -1:
                snapped.setX(rect.x())
                snapped.setY(rect.y())
            snapped.setWidth(abs((rect.x() + rect.width()) - snapped.x()))
            snapped.setHeight(abs((rect.y() + rect.height()) - snapped.y()))
    do_grid(grid, grid_callback)
    # created translated point to the monitor
    translated = QtCore.QRect(-1, -1, -1, -1)
    translated.setX((float(snapped.x()) / grid.width()) * float(active_region.width()))
    translated.setY((float(snapped.y()) / grid.height()) * float(active_region.height()))
    translated.setWidth((float(snapped.width()) / grid.width()) * float(active_region.width()))
    translated.setHeight((float(snapped.height()) / grid.height()) * float(active_region.height()))
    # move the window
    change_window_region(active_region, wid, translated)
    # hide the program window
    window.hide()


# snaps the window to the left side of the screen at 50% width and 100% height
def snap_left_50(window, grid, active_region, active_window, drag):
    drag.setRect(0, 0, grid.width() / 2, grid.height())
    size_and_hide(window, grid, active_region, active_window, drag)


# snaps the window to the right side of the screen at 50% width and 100% height
def snap_right_50(window, grid, active_region, active_window, drag):
    drag.setRect(grid.width() / 2, 0, grid.width() / 2, grid.height())
    size_and_hide(window, grid, active_region, active_window, drag)
    

# snaps the window to the top side of the screen at 100% width and 50% height
def snap_top_50(window, grid, active_region, active_window, drag):
    drag.setRect(0, 0, grid.width(), grid.height() / 2)
    size_and_hide(window, grid, active_region, active_window, drag)


# snaps the window to the bottom side of the screen at 100% width and 50% height
def snap_bot_50(window, grid, active_region, active_window, drag):
    drag.setRect(0, grid.height() / 2, grid.width(), grid.height() / 2)
    size_and_hide(window, grid, active_region, active_window, drag)


# creates the GUI used to change window regions
def create_grid_gui(app):
    active_region = active_screen_region(app)
    active_window = WinData.active_window_id()

    window = QtWidgets.QDialog()

    # set window flagsfsdf
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                        QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool | 
                        QtCore.Qt.X11BypassWindowManagerHint)

    # set window properties
    window.setFixedSize(300, 300)
    window.setStyleSheet('background-color: rgb(%s, %s, %s)' % (FRAME_COLOR.red(), FRAME_COLOR.green(), FRAME_COLOR.blue()))
    window.setWindowOpacity(0.9)

    # set window layout
    layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, window)

    # create grid component
    grid = QtWidgets.QFrame()
    grid.setFixedSize(280, 280)
    grid.setStyleSheet('background-color: rgb(%s, %s, %s)' % (GRID_BG_COLOR.red(), GRID_BG_COLOR.green(), GRID_BG_COLOR.blue()))

    # setup drag bounds
    drag = QtCore.QRect(-1, -1, -1, -1)

    # create grid drawer
    def override_paint_event(evt):
        # create the painter
        painter = QtGui.QPainter(grid)
        # create the grid callback
        def grid_callback(rect):
            painter.setPen(QtGui.QPen(GRID_COLOR))
            painter.drawRect(rect)
            if rect.intersects(drag):
                painter.fillRect(rect, REGION_COLOR)
        # draw the grid
        do_grid(grid, grid_callback)
        # draw axis
        painter.setPen(QtGui.QPen(FRAME_COLOR))
        painter.drawLine(grid.width() / 2, 0, grid.width() / 2, grid.height())
        painter.drawLine(0, grid.height() / 2, grid.width(), grid.height() / 2)
    grid.paintEvent = override_paint_event

    initial = QtCore.QPoint(-1, -1)

    # create grid drag listeners
    def override_mouse_press_event(evt):
        initial.setX(evt.pos().x())
        initial.setY(evt.pos().y())
    def override_mouse_move_event(evt):
        drag.setWidth(abs(evt.pos().x() - initial.x()))
        drag.setHeight(abs(evt.pos().y() - initial.y()))
        drag.setX(min(evt.pos().x(), initial.x()))
        drag.setY(min(evt.pos().y(), initial.y()))
        grid.repaint()
    def override_mouse_release_event(evt):
        size_and_hide(window, grid, active_region, active_window, drag)
    grid.mousePressEvent = override_mouse_press_event
    grid.mouseMoveEvent = override_mouse_move_event
    grid.mouseReleaseEvent = override_mouse_release_event

    # add grid
    layout.addWidget(grid, QtCore.Qt.AlignCenter)

    # grab focus upon showing
    def override_show_event(evt):
        window.raise_()
        window.activateWindow()
        window.setFocus()
    window.showEvent = override_show_event

    # exit the program upon hiding
    def override_hide_event(evt):
        window.close()
        app.exit() # close the program since it is a one-run type of program
    window.hideEvent = override_hide_event

    # allow escape to quit the program
    def override_key_press_event(evt):
        if evt.key() == QtCore.Qt.Key_Escape:
            window.hide()
        elif evt.key() == QtCore.Qt.Key_W or evt.key() == QtCore.Qt.Key_Up:
            snap_top_50(window, grid, active_region, active_window, drag)
        elif evt.key() == QtCore.Qt.Key_A or evt.key() == QtCore.Qt.Key_Left:
            snap_left_50(window, grid, active_region, active_window, drag)
        elif evt.key() == QtCore.Qt.Key_S or evt.key() == QtCore.Qt.Key_Down:
            snap_bot_50(window, grid, active_region, active_window, drag)
        elif evt.key() == QtCore.Qt.Key_D or evt.key() == QtCore.Qt.Key_Right:
            snap_right_50(window, grid, active_region, active_window, drag)

    window.keyPressEvent = override_key_press_event

    # center the window and show it
    mid_x = (active_region.topLeft().x() + (active_region.width() / 2)) - (window.width() / 2)
    mid_y = (active_region.height() / 2) - (window.height() / 2)

    window.move(mid_x, mid_y)
    window.show()
    
    return window


# main program logic
def main():
    app = QtWidgets.QApplication([])
    create_grid_gui(app)
    app.exec_()


if __name__ == '__main__':
    main()