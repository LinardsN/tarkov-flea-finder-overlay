from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QComboBox, QDialogButtonBox, QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QFont

class SettingsPopup(QDialog):
    settings_applied = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.container)

        label_font = QFont("Arial", 14)
        label_font.setBold(True)

        opacity_label = QLabel("Opacity:")
        opacity_label.setFont(label_font)
        opacity_label.setStyleSheet("color: white;")
        self.container_layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(50)
        self.opacity_slider.setMaximum(255)
        self.opacity_slider.setValue(255)
        self.container_layout.addWidget(self.opacity_slider)

        color_scheme_label = QLabel("Color Scheme:")
        color_scheme_label.setFont(label_font)
        color_scheme_label.setStyleSheet("color: white;")
        self.container_layout.addWidget(color_scheme_label)

        self.color_scheme_combobox = QComboBox()
        self.color_scheme_combobox.addItem("Default")
        self.color_scheme_combobox.addItem("Alternative")
        self.color_scheme_combobox.setStyleSheet("""
            QComboBox {
                color: white;
            }
            QComboBox QAbstractItemView {
                color: white;
                background-color: rgba(40, 40, 40, 230);
                selection-background-color: rgba(70, 70, 70, 230);
            }
        """)  # Set the dropdown text color to white
        self.container_layout.addWidget(self.color_scheme_combobox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.apply_and_close)
        self.container_layout.addWidget(button_box)

        self.apply_styles()

    def apply_styles(self):
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 230);
                border: 2px solid #8795A1;
                border-radius: 5px;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def apply_and_close(self):
        opacity = self.opacity_slider.value()
        color_scheme = self.color_scheme_combobox.currentText()
        self.settings_applied.emit(opacity, color_scheme)
        self.accept()
