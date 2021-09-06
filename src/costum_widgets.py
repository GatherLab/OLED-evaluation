from PySide2 import QtWidgets, QtCore, QtGui

from PySide2.QtCore import QPropertyAnimation, QRectF, QSize, Qt, Property
from PySide2.QtGui import QPainter, QColor, QPalette
from PySide2.QtWidgets import (
    QAbstractButton,
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

import time


class Ui_GoniometerAnimation(QtWidgets.QWidget):
    """
    This class represents the goniometer animation that shows the current
    position of the motor stage. It is used to update and draw the animation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )

        # Initial position
        self.position = 0

    def sizeHint(self):
        """
        Function needed to scale the widget
        """
        return QtCore.QSize(40, 140)

    def paintEvent(self, e):
        """
        Paint event that is called when the update function is called on the class
        """
        painter = QtGui.QPainter(self)

        # Set a plain background in the overall design color
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("#2C313C"))
        brush.setStyle(QtCore.Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)
        rect.center()

        # The following looks relatively complicated but in the end it is just
        # some calculations to make the drawing look nice and have everything
        # at its right position
        circle_radius = 52
        circle_thickness = 4
        letter_width = 6
        letter_height = 9
        arc_thickness = 8
        margin = 2

        painter.setPen(
            QtGui.QPen(QtGui.QColor("#E0E0E0"), circle_thickness, QtCore.Qt.SolidLine)
        )
        painter.drawEllipse(rect.center(), circle_radius, circle_radius)
        painter.drawText(
            rect.center().toTuple()[0] + circle_radius + circle_thickness + margin,
            rect.center().toTuple()[1] + letter_height / 2,
            "0°",
        )
        # painter.drawText(
        # rect.center().toTuple()[0]
        # - circle_radius
        # - circle_thickness
        # - margin
        # - letter_width * len(str("180°")),
        # rect.center().toTuple()[1] + letter_height / 2,
        # "180°",
        # )

        painter.drawText(
            rect.center().toTuple()[0] - letter_width * len(str("90°")) / 2,
            rect.center().toTuple()[1] - circle_radius - circle_thickness - margin,
            "90°",
        )
        painter.drawText(
            rect.center().toTuple()[0] - letter_width * len(str("-90°")) / 2,
            rect.center().toTuple()[1]
            + circle_radius
            + circle_thickness
            + margin
            + letter_height,
            "-90°",
        )

        painter.setPen(
            QtGui.QPen(QtGui.QColor("#55AAFF"), arc_thickness, QtCore.Qt.SolidLine)
        )
        painter.drawArc(
            rect.center().toTuple()[0]
            - circle_radius
            + (circle_thickness + arc_thickness + margin) / 2,
            rect.center().toTuple()[1]
            - circle_radius
            + (circle_thickness + arc_thickness + margin) / 2,
            circle_radius * 2 - margin - circle_thickness - arc_thickness,
            circle_radius * 2 - margin - circle_thickness - arc_thickness,
            0 * 16,
            16 * self.position,
        )
        painter.drawText(
            rect.center().toTuple()[0]
            - letter_width * len(str(self.position) + "°") / 2,
            rect.center().toTuple()[1] + letter_height / 2,
            str(self.position) + "°",
        )
        painter.end()
        time.sleep(0.05)

    def _trigger_refresh(self):
        self.update()

    @QtCore.Slot(float)
    def move(self, position):
        """
        Function to trigger a move of the position animation for the goniometer
        """
        self.position = round(position, 1)
        self.update()


class ToggleSwitch(QAbstractButton):
    """
    Toggle switch modified from
    https://stackoverflow.com/questions/14780517/toggle-switch-in-qt/51023362
    """

    def __init__(self, parent=None, track_radius=10, thumb_radius=8):
        super().__init__(parent=parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._track_radius = track_radius
        self._thumb_radius = thumb_radius

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        # Set the colors of the toggle switch
        palette = self.palette()
        palette.setColor(QPalette.Highlight, QColor(85, 170, 255))
        self.setPalette(palette)
        self.update()

        if self._thumb_radius > self._track_radius:
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumb_color = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._text_color = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: "",
                False: "",
            }
            self._track_opacity = 0.5
        else:
            self._thumb_color = {
                True: palette.highlightedText(),
                False: palette.light(),
            }
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._text_color = {
                True: palette.highlight().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: "✔",
                False: "✕",
            }
            self._track_opacity = 1

    # @Property(int)
    def offsetGet(self):
        return self._offset

    # @offset.setter
    def offsetSet(self, value):
        self._offset = value
        self.update()

    offset = Property(int, offsetGet, offsetSet)

    def sizeHint(self):  # pylint: disable=invalid-name
        return QSize(
            4 * self._track_radius + 2 * self._margin,
            2 * self._track_radius + 2 * self._margin,
        )

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]()

    def paintEvent(self, event):  # pylint: disable=invalid-name, unused-argument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        text_opacity = 1.0
        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
            text_color = self._text_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()
            text_color = self.palette().shadow().color()

        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
            self._track_radius,
            self._track_radius,
        )
        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        p.drawEllipse(
            self.offset - self._thumb_radius,
            self._base_offset - self._thumb_radius,
            2 * self._thumb_radius,
            2 * self._thumb_radius,
        )
        p.setPen(text_color)
        p.setOpacity(text_opacity)
        font = p.font()
        font.setPixelSize(1.5 * self._thumb_radius)
        p.setFont(font)
        p.drawText(
            QRectF(
                self.offset - self._thumb_radius,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            anim = QPropertyAnimation(self, b"offset", self)
            anim.setDuration(120)
            anim.setStartValue(self.offset)
            anim.setEndValue(self._end_offset[self.isChecked()]())
            anim.start()

    def enterEvent(self, event):  # pylint: disable=invalid-name
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


# def main():
#     app = QApplication([])

#     # Thumb size < track size (Gitlab style)
#     s1 = Switch()
#     s1.toggled.connect(lambda c: print("toggled", c))
#     s1.clicked.connect(lambda c: print("clicked", c))
#     s1.pressed.connect(lambda: print("pressed"))
#     s1.released.connect(lambda: print("released"))
#     s2 = Switch()
#     s2.setEnabled(False)

#     # Thumb size > track size (Android style)
#     s3 = Switch(thumb_radius=11, track_radius=8)
#     s4 = Switch(thumb_radius=11, track_radius=8)
#     s4.setEnabled(False)

#     l = QHBoxLayout()
#     l.addWidget(s1)
#     l.addWidget(s2)
#     l.addWidget(s3)
#     l.addWidget(s4)
#     w = QWidget()
#     w.setLayout(l)
#     w.show()

#     app.exec_()


# if __name__ == "__main__":
#     main()


class HumbleDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args):
        super(HumbleDoubleSpinBox, self).__init__(*args)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusInEvent(self, event):
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        super(HumbleDoubleSpinBox, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        super(HumbleDoubleSpinBox, self).focusOutEvent(event)

    def wheelEvent(self, event):
        if self.hasFocus():
            return super(HumbleDoubleSpinBox, self).wheelEvent(event)
        else:
            event.ignore()


class HumbleSpinBox(QtWidgets.QSpinBox):
    def __init__(self, *args):
        super(HumbleSpinBox, self).__init__(*args)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusInEvent(self, event):
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        super(HumbleSpinBox, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        super(HumbleSpinBox, self).focusOutEvent(event)

    def wheelEvent(self, event):
        if self.hasFocus():
            return super(HumbleSpinBox, self).wheelEvent(event)
        else:
            event.ignore()