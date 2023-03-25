from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QCompleter, QSlider, QSpinBox, QComboBox, QDialogButtonBox
from PyQt5.QtCore import Qt, QTimer, QPoint, QStringListModel, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5 import QtWidgets
import api
import os
import os.path
from settings_popup import SettingsPopup

class Overlay(QDialog):
    keep_focus = pyqtSignal()

    def __init__(self, item_list):
        super().__init__()
        self.item_list = item_list
        self.drag_position = QPoint()
        self.initUI()
        self.image_cache = {}

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        content_font = QFont("Arial", 12)

        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.container)

        title_bar = QHBoxLayout()
        title = QLabel('Tarkov Market Overlay')
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        title_bar.addWidget(title)
        title_bar.addStretch()

        gear_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.png')

        settings_button = QPushButton()
        settings_button.setIcon(QIcon(gear_icon_path))
        settings_button.setFixedWidth(25)
        settings_button.setStyleSheet("color: white; background-color: transparent;")
        settings_button.clicked.connect(self.show_settings)
        title_bar.addWidget(settings_button)

        close_button = QPushButton('X')
        close_button.setFont(title_font)
        close_button.setFixedWidth(25)
        close_button.setStyleSheet("color: white; background-color: transparent;")
        close_button.clicked.connect(self.hide)
        title_bar.addWidget(close_button)

        self.container_layout.addLayout(title_bar)

        self.label = QLabel('Enter item name:', self)
        self.label.setFont(content_font)
        self.label.setStyleSheet("color: white;")
        
        self.item_image = QLabel(self)
        self.item_image.setFixedSize(64, 64)
        self.item_image.setStyleSheet("background-color: transparent;")

        self.info_layout = QHBoxLayout()
        self.container_layout.addLayout(self.info_layout)
        self.info_layout.addWidget(self.label)
        self.info_layout.addWidget(self.item_image)

        self.search_input = QLineEdit(self)
        self.container_layout.addWidget(self.search_input)
        self.search_input.returnPressed.connect(self.handle_return_pressed)

        self.setup_completer()
        self.apply_styles()

        self.container_layout.addStretch()

        self.container_layout.setSpacing(10)

        self.trademark_label = QLabel('Developed by LN. All rights reserved.', self)
        self.trademark_label.setFont(QFont("Arial", 8))
        self.trademark_label.setAlignment(Qt.AlignCenter)
        self.trademark_label.setFixedWidth(250)
        self.trademark_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.trademark_label.setStyleSheet("color: white;")
        self.container_layout.addWidget(self.trademark_label, 0, Qt.AlignCenter)

    def handle_return_pressed(self):
        if not self.search_input.text().strip():
            self.search_input.setFocus()
            return
        self.search_and_keep_focus()



    def setup_completer(self):
        item_names = [item["name"] for item in self.item_list]
        completer = QCompleter()
        model = QStringListModel()
        model.setStringList(item_names)
        completer.setModel(model)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(20)
        self.search_input.setCompleter(completer)
        self.update_popup_height()
        completer.popup().setMinimumWidth(self.search_input.width())

        completer.activated.connect(self.handle_completer_activated)

    def handle_completer_activated(self, text):
        self.search_input.setText(text)
        self.search_and_keep_focus()
        QTimer.singleShot(0, self.search_input.clear)



    def apply_styles(self):
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 230);
                border: 2px solid #8795A1;
                border-radius: 5px;
            }
           """)

        self.search_input.setStyleSheet("""
            QLineEdit {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 50);
                border: 1px solid #8795A1;
                border-radius: 3px;
            }
        """)
    
    def set_item_image(self, url):
        if url:
            if url in self.image_cache:
                self.item_image.setPixmap(self.image_cache[url])
            else:
                network_manager = QNetworkAccessManager(self)
                network_manager.finished.connect(self.set_image_data)
                network_request = QNetworkRequest(QUrl(url))
                network_manager.get(network_request)
        else:
            self.item_image.clear()


    def set_image_data(self, reply):
        url = reply.url().toString()
        image_data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio)
        self.item_image.setPixmap(pixmap)
        self.image_cache[url] = pixmap


    def show_settings(self):
        settings_dialog = SettingsPopup(self)
        settings_dialog.setWindowTitle("Settings")
        settings_dialog.setModal(True)
        settings_dialog.exec_()

        layout = QVBoxLayout()
        settings_dialog.container_layout.addLayout(layout)

        # Opacity slider
        opacity_label = QLabel("Opacity:")
        layout.addWidget(opacity_label)
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMinimum(50)
        opacity_slider.setMaximum(255)
        opacity_slider.setValue(int(self.windowOpacity() * 255))
        opacity_slider.valueChanged.connect(lambda value: self.setWindowOpacity(value / 255))
        layout.addWidget(opacity_slider)

        # Color scheme dropdown
        color_scheme_label = QLabel("Color Scheme:")
        layout.addWidget(color_scheme_label)
        color_scheme_combobox = QComboBox()
        color_scheme_combobox.addItem("Default")
        color_scheme_combobox.addItem("Alternative")
        color_scheme_combobox.currentTextChanged.connect(lambda text: self.change_color_scheme(text))
        layout.addWidget(color_scheme_combobox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(settings_dialog.accept)
        layout.addWidget(button_box)

        settings_dialog.exec_()

    def change_font_size(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def change_color_scheme(self, scheme):
        if scheme == "Default":
            self.apply_styles()
        elif scheme == "Alternative":
            self.apply_alternative_styles()

    def apply_alternative_styles(self):
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 60, 230);
                border: 2px solid #8795A1;
                border-radius: 5px;
            }
        """)

        self.search_input.setStyleSheet("""
            QLineEdit {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 50);
                border: 1px solid #8795A1;
                border-radius: 3px;
            }
        """)


    def update_popup_height(self):
        popup = self.search_input.completer().popup()
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        max_visible_items = min(len(self.item_list), 20)
        item_height = popup.sizeHintForRow(0)

        popup_height = max_visible_items * item_height + 2 * popup.frameWidth()
        popup.setFixedHeight(popup_height)

    def clear_search_input(self, _):
        self.search_input.clear()

    def search_and_keep_focus(self):
        item_name = self.search_input.text()
        item = self.fetch_item(item_name)

        if item:
            self.label.setText(f'{item["name"]} ({item["shortName"]})\nBase Price: {item["basePrice"]}\nAvg 24h Flea Price: {item["avg24hPrice"]}')
            self.set_item_image(item.get("gridImageLink"))
            self.search_input.clear()
        else:
            self.label.setText('Item not found.')
            self.search_input.clear()

        self.search_input.setFocus()  # Always set the focus back to the search input


    def fetch_item(self, input_text):
        for item in self.item_list:
            if item["name"].lower() == input_text.lower() or item["shortName"].lower() == input_text.lower():
                item_data = api.fetch_item(item["name"])
                if item_data:
                    return {
                        "name": item_data["name"],
                        "shortName": item_data["shortName"],
                        "id": item_data["id"],
                        "basePrice": item_data["basePrice"],
                        "avg24hPrice": item_data["avg24hPrice"],
                        "gridImageLink": item_data["gridImageLink"],
                    }
        return None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            event.ignore()
            self.search_input.setFocus()
        else:
            super().keyPressEvent(event)


