import sys
import os
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import keyboard
import pyautogui
from api import fetch_item_list, fetch_item
from overlay import Overlay

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_key_press(overlay):
    if keyboard.is_pressed('down') and not overlay.isVisible():
        overlay.show()

    if keyboard.is_pressed('left'):
        mouse_x, mouse_y = pyautogui.position()
        region_x = mouse_x - 100
        region_y = mouse_y - 100
        region_width = 200
        region_height = 200
        screenshot = pyautogui.screenshot(region=(region_x, region_y, region_width, region_height))
        print('Screenshot taken')
        item_name = recognize_item(screenshot, overlay)
        if item_name:
            recognize_item(screenshot, overlay)

def preprocess_image(image):
    image = image.convert('L')  # Convert to grayscale
    image = image.filter(ImageFilter.MedianFilter())  # Apply a median filter to reduce noise
    threshold = 180
    image = image.point(lambda p: p > threshold and 255)  # Apply thresholding
    image = image.resize((2*image.width, 2*image.height), Image.BICUBIC)  # Resize the image
    return image

def post_process_text(text):
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines
    return ' '.join(lines)  # Join lines into a single string

def recognize_item(screenshot, overlay):
    # Preprocess the image
    processed_image = preprocess_image(screenshot)

    # Recognize text using Tesseract with specific configuration
    text = pytesseract.image_to_string(processed_image, lang='eng', config='--psm 6 --oem 3')

    # Post-process the recognized text
    item_name = post_process_text(text)

    # Set the text and focus on the search input field
    overlay.search_input.setText(item_name)
    overlay.search_and_keep_focus()
    print('Recognized text:', text)
    return item_name

app = QApplication(sys.argv)
item_list = fetch_item_list()
overlay = Overlay(item_list)

timer = QTimer()
timer.timeout.connect(lambda: check_key_press(overlay))
timer.start(100)

sys.exit(app.exec_())
