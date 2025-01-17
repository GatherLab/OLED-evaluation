from PySide6 import QtWidgets, QtCore, QtGui


# This class has to be defined to obtain a labeled slider used in the group
# assigned dialog. The predefined slider of pyqt has no labels. This solution
# was copied from stackoverflow.com
class LabeledSlider(QtWidgets.QWidget):
    def __init__(
        self,
        minimum,
        maximum,
        interval=1,
        orientation=QtCore.Qt.Horizontal,
        labels=None,
        parent=None,
    ):
        # Initialize the labeled slider

        super(LabeledSlider, self).__init__(parent=parent)

        levels = range(minimum, maximum + interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, labels))
        else:
            self.levels = list(zip(levels, map(str, levels)))

        if orientation == QtCore.Qt.Horizontal:
            self.layout = QtWidgets.QVBoxLayout(self)
        elif orientation == QtCore.Qt.Vertical:
            self.layout = QtWidgets.QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.layout.setContentsMargins(
            self.left_margin, self.top_margin, self.right_margin, self.bottom_margin
        )

        self.sl = QtWidgets.QSlider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        self.sl.setValue(minimum)
        if orientation == QtCore.Qt.Horizontal:
            self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.sl.setMinimumWidth(300)  # just to make it easier to read
        else:
            self.sl.setTickPosition(QtWidgets.QSlider.TicksLeft)
            self.sl.setMinimumHeight(300)  # just to make it easier to read
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)

        self.layout.addWidget(self.sl)

    def setValue(self, nb):
        # From the python code set a new value

        self.sl.setValue(nb)

    def valueChanged(self, function):
        # Overload the value changed function of the predefined slider

        self.sl.valueChanged.connect(function)

    def value(self):
        # Overload the value function of the predefined slider

        return self.sl.value()

    def paintEvent(self, e):
        # Paint the numbers below the slider

        super(LabeledSlider, self).paintEvent(e)

        style = self.sl.style()
        painter = QtGui.QPainter(self)
        st_slider = QtWidgets.QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QtWidgets.QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(
            QtWidgets.QStyle.PM_SliderSpaceAvailable, st_slider, self.sl
        )

        for v, v_str in self.levels:

            # get the size of the label
            rect = painter.drawText(QtCore.QRect(), QtCore.Qt.TextDontPrint, v_str)

            if self.sl.orientation() == QtCore.Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = (
                    QtWidgets.QStyle.sliderPositionFromValue(
                        self.sl.minimum(), self.sl.maximum(), v, available
                    )
                    + length // 2
                )

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - rect.width() // 2 + self.left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_margin = rect.width() // 2 - x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()

                    self.layout.setContentsMargins(
                        self.left_margin,
                        self.top_margin,
                        self.right_margin,
                        self.bottom_margin,
                    )

                if v == self.sl.maximum() and rect.width() // 2 >= self.right_margin:
                    self.right_margin = rect.width() // 2
                    self.layout.setContentsMargins(
                        self.left_margin,
                        self.top_margin,
                        self.right_margin,
                        self.bottom_margin,
                    )

            else:
                y_loc = QtWidgets.QStyle.sliderPositionFromValue(
                    self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True
                )

                bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin - rect.width()
                if left <= 0:
                    self.left_margin = rect.width() + 2
                    self.layout.setContentsMargins(
                        self.left_margin,
                        self.top_margin,
                        self.right_margin,
                        self.bottom_margin,
                    )

            pos = QtCore.QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return
