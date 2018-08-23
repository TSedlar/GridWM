from PySide2 import QtWidgets, QtGui, QtCore
import window_data as WinData
import time
import types


BLOCKS = 20
MARGIN = 50
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


# creates the GUI used to change window regions
def create_grid_gui(app):
    active_region = active_screen_region(app)
    active_window = WinData.active_window_id()

    window = QtWidgets.QWidget()

    # set window flags
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
    translated = QtCore.QRect(-1, -1, -1, -1)

    # grid data
    blocks = BLOCKS
    margin = MARGIN
    size = int(grid.width() / blocks)

    # create grid drawer
    def override_paint_event(evt):
        # draw the grid and fixate the dragged rectangle to a snapped grid
        snapped = QtCore.QRect(-1, -1, -1, -1)
        painter = QtGui.QPainter(grid)
        for x in range(0, blocks):
            for y in range(0, blocks):
                rect = QtCore.QRect(x * size, y * size, size, size)
                painter.setPen(QtGui.QPen(GRID_COLOR))
                painter.drawRect(rect)
                if rect.intersects(drag):
                    if snapped.x() == -1 or snapped.y() == -1:
                        snapped.setX(rect.x())
                        snapped.setY(rect.y())
                    snapped.setWidth(abs((rect.x() + rect.width()) - snapped.x()))
                    snapped.setHeight(abs((rect.y() + rect.height()) - snapped.y()))
                    painter.fillRect(rect, REGION_COLOR)

        # draw axis
        painter.setPen(QtGui.QPen(FRAME_COLOR))
        painter.drawLine(grid.width() / 2, 0, grid.width() / 2, grid.height())
        painter.drawLine(0, grid.height() / 2, grid.width(), grid.height() / 2)

        # created translated point to the monitor
        translated.setX((float(snapped.x()) / grid.width()) * float(active_region.width()))
        translated.setY((float(snapped.y()) / grid.height()) * float(active_region.height()))
        translated.setWidth((float(snapped.width()) / grid.width()) * float(active_region.width()))
        translated.setHeight((float(snapped.height()) / grid.height()) * float(active_region.height()))
    grid.paintEvent = override_paint_event

    initial = QtCore.QPoint(-1, -1)

    # create grid drag listener
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
        top = active_region.topLeft()
        print(active_region)
        tx = int(top.x() + translated.x() + (margin / 2.0))
        ty = int(translated.y() + (margin / 2.0)) + top.y()
        tw = (translated.width() - margin)
        th = (translated.height() - margin) - top.y()
        neg = (margin / (blocks / 4.0))
        distFromLeft = abs(tx - top.x())
        distFromRight = abs((tx + tw) - (top.x() + active_region.width()))
        distFromTop = abs(ty - top.y())
        distFromBot = abs((ty + th) - (active_region.height()))
        if distFromLeft < margin:
            tx += neg
        if distFromRight < margin:
            tx -= neg
        if distFromTop < margin:
            ty += neg
        if distFromBot < margin:
            ty -= neg
        WinData.move_window(active_window, tx, ty)
        WinData.size_window(active_window, tw, th)
        window.hide()
    grid.mousePressEvent = override_mouse_press_event
    grid.mouseMoveEvent = override_mouse_move_event
    grid.mouseReleaseEvent = override_mouse_release_event

    # give the grid mouse focus
    grid.grabMouse()

    # add grid
    layout.addWidget(grid, QtCore.Qt.AlignCenter)

    # center the window
    mid_x = (active_region.topLeft().x() + (active_region.width() / 2)) - (window.width() / 2)
    mid_y = (active_region.height() / 2) - (window.height() / 2)

    window.move(mid_x, mid_y)

    window.show()

    # give the window key focus
    window.setFocusPolicy(QtCore.Qt.StrongFocus)
    window.setFocus()
    window.focusWidget()
    window.grabKeyboard()

    # release keyboard/mouse focus on hiding
    def override_hide_event(evt):
        grid.releaseMouse()
        window.releaseKeyboard()
        app.exit() # close the program since it is a one-run type of program
    window.hideEvent = override_hide_event

    # allow escape to quit the program
    def override_key_press_event(evt):
        if evt.key() == QtCore.Qt.Key_Escape:
            window.hide()

    window.keyPressEvent = override_key_press_event
    
    return window


# main program logic
def main():
    app = QtWidgets.QApplication([])
    create_grid_gui(app)
    app.exec_()


if __name__ == '__main__':
    main()