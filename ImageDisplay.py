from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsSceneMouseEvent
import cv2
import numpy as np
import logging
logging.basicConfig(filename='user.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageDisplay:

    image_indexes = []
    def __init__(self, label, image_component, combo_box = None, out_combo_box = None, insideButton = None, value = None):
        self.label = label
        self.image_component = image_component
        self.combo_box = combo_box
        self.out_combo_box = out_combo_box
        self.insideButton = insideButton
        self.value = value
        self.last_click_time = 0
        ImageDisplay.image_indexes.append(self)

        self.mouse_pressed = False
        self.last_pos = None
        self.brightness_adjustment = 0
        self.contrast_adjustment = 0

        self.label.setMouseTracking(True)
        self.label.mouseMoveEvent = self.handle_mouse_move
        self.label.mousePressEvent = self.handle_mouse_press
        self.label.mouseReleaseEvent = self.handle_mouse_release


    def handle_mouse_press(self, event):
        if event.button() == Qt.RightButton:
            self.reset_adjustments()
        else:
            self.mouse_pressed = True
            self.last_pos = event.pos()

    def reset_adjustments(self):
        self.last_pos = None
        self.brightness_adjustment = 0
        self.contrast_adjustment = 0
        self.set_image_from_array(self.original_image)

    def handle_mouse_move(self, event):
        if self.mouse_pressed:
            current_pos = event.pos()
            delta = current_pos - self.last_pos
            self.handle_brightness(delta.y())
            self.handle_contrast(delta.x())
            self.last_pos = current_pos

    def handle_mouse_release(self, event):
        self.mouse_pressed = False

    def handle_brightness(self, delta):
        brightness_change = int(delta / 5)
        self.brightness_adjustment += brightness_change
        adjusted_image = np.clip(self.resized_image + self.brightness_adjustment, 0, 255)
        self.set_image_from_array(adjusted_image)

    def handle_contrast(self, delta):
        contrast_change = delta / 10.0
        self.contrast_adjustment += contrast_change
        adjusted_image = cv2.addWeighted(self.resized_image, 1.0 + self.contrast_adjustment, 0, 0, 0)
        self.set_image_from_array(adjusted_image)

    def set_image_from_array(self, image_array):
        # Display the image from a NumPy array
        resized_image = cv2.resize(image_array, (self.label.width(), self.label.height() + self.value),
                                   interpolation=cv2.INTER_AREA)

        # Convert the image array to QImage and display it in the QGraphicsView
        q_image = QImage(resized_image.data, resized_image.shape[1], resized_image.shape[0], QImage.Format_Grayscale8)
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)
        self.label.setScene(scene)
        self.label.fitInView(pixmap_item, Qt.KeepAspectRatio)

    def on_label_double_clicked(self, event):
        current_time = QDateTime.currentMSecsSinceEpoch()
        if current_time - self.last_click_time < 5000:
            self.open_image_dialog()
        self.last_click_time = current_time

    def open_image_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp *.jpeg)")
        file_dialog.setWindowTitle("Open Image File")

        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            self.image_path = selected_file  
            self.set_image(selected_file)

    def set_image(self, path):
        logging.info(f'User selected image in path: {path}')
        try:
            self.original_image = cv2.imdecode(np.frombuffer(open(path, 'rb').read(), np.uint8), cv2.IMREAD_GRAYSCALE)
            logging.info(f'Image is loaded from path: {path}')
        except Exception as e:
            logging.error(f'Error loading image from path {path}: {str(e)}')
            return
        self.resized_image = cv2.resize(self.original_image, (self.label.width(), self.label.height()+self.value), interpolation=cv2.INTER_AREA)
        logging.info('Image selected is displayed.')
        height, width = self.resized_image.shape
        bytes_per_line = width
        q_image = QImage(self.resized_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)
        self.label.setScene(scene)
        self.label.fitInView(pixmap_item, Qt.KeepAspectRatio)

        fourier_transform = np.fft.fft2(self.resized_image)
        self.fourier_shift = np.fft.fftshift(fourier_transform)
        selected_index = self.combo_box.currentIndex()
        logging.info(f'Displaying Ft magnitude of the image')
        self.set_transformed_image_by_index(selected_index)

    def handle_combobox_change(self):
        image_index = self.image_indexes.index(self) + 1
        if self.combo_box is not None:
            selected_index = self.combo_box.currentIndex()

            if selected_index == 0:
                logging.info(f'Ft magnitude of Image {image_index} is chosen to be displayed')
            elif selected_index == 1:
                logging.info(f'Ft Phase of Image {image_index} is chosen to be displayed')
            elif selected_index == 2:
                logging.info(f'Ft Real of Image {image_index} is chosen to be displayed')
            else:
                logging.info(f'Ft Imaginary of Image {image_index} is chosen to be displayed')

            self.set_transformed_image_by_index(selected_index)


    def set_transformed_image_by_index(self, index):
        if index == 0:  # Magnitude
            self.transformed_image = np.multiply(np.log10(1 + np.abs(self.fourier_shift)), 20)
        elif index == 1:  # Phase
            self.transformed_image = np.angle(self.fourier_shift)
        elif index == 2:  # Real
            self.transformed_image = np.real(self.fourier_shift)
        elif index == 3:  # Imaginary
            self.transformed_image = np.imag(self.fourier_shift)
        else:      # Magnitude
            self.transformed_image = np.multiply(np.log10(1 + np.abs(self.fourier_shift)), 20)

        self.updateDisplay(self.transformed_image)

    def updateDisplay(self, transformed_image):
        resized_transformed = cv2.resize(transformed_image, (self.image_component.width(), self.image_component.height()), interpolation=cv2.INTER_AREA)
        resized_transformed_bytes = resized_transformed.astype(np.uint8).tobytes()
        height, width = resized_transformed.shape
        # print(height, width)
        bytes_per_line = width
        q_image = QImage(resized_transformed_bytes, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)
        self.addResizableRectangle(scene, pixmap_item)
        self.image_component.setScene(scene)
        self.image_component.fitInView(pixmap_item, Qt.KeepAspectRatio)

    def addResizableRectangle(self, scene, pixmap_item):
        self.rect_item = QGraphicsRectItem(0, 0, 50, 50)
        self.rect_item.setPen(QPen(Qt.red))
        brush = QBrush(QColor(255, 0, 0, 50))
        self.rect_item.setBrush(brush)
        self.rect_item.setPos((self.image_component.width() - self.rect_item.rect().width()) / 2,
                              (self.image_component.height() - self.rect_item.rect().height()) / 2)
        scene.addItem(self.rect_item)

    def ExtractRegion(self):
        self.fshiftcopy = self.fourier_shift
        # Get the rectangle's position and size in scene coordinates
        rect_scene_pos = self.rect_item.scenePos()
        rect_scene_rect = self.rect_item.rect()

        # Convert rectangle position and size to image coordinates
        rect_image_pos = self.image_component.mapFromScene(rect_scene_pos)
        rect_image_rect = self.image_component.mapFromScene(rect_scene_rect).boundingRect()

        # Create a mask with zeros everywhere except in the rectangle region
        if self.insideButton.isChecked():
            self.mask = np.zeros_like(self.fourier_shift)
            self.mask[int(rect_image_pos.y()):int(rect_image_pos.y() + rect_image_rect.height()),
                int(rect_image_pos.x()):int(rect_image_pos.x() + rect_image_rect.width())] = 1
        else:
            self.mask = np.ones_like(self.fourier_shift)
            self.mask[int(rect_image_pos.y()):int(rect_image_pos.y() + rect_image_rect.height()),
                int(rect_image_pos.x()):int(rect_image_pos.x() + rect_image_rect.width())] = 0
            
        self.fshiftcopy = self.fourier_shift * self.mask

    def update_rect_size(self, new_width, new_height):
        self.rect_item.setRect(0, 0, new_width, new_height)
        self.rect_item.setPos((self.image_component.width() - new_width) / 2,
                              (self.image_component.height() - new_height) / 2)
        self.ExtractRegion()

    def get_component(self, component):
        if self.fshiftcopy is None:
            return None , None
        if component== "Magnitude/Phase":
            return np.abs( self.fshiftcopy), np.angle( self.fshiftcopy)
        elif component== "Real/Imaginary":
            return np.real( self.fshiftcopy), np.imag( self.fshiftcopy)
    @staticmethod
    def combination(img_1, img_2, img_3, img_4, index, slider_1, slider_2, slider_3, slider_4, list_combo_box):      #refactored
        mixing_list1, mixing_list2 = [], []
        newmag, newphase, newreal, newimag = 0, 0, 0, 0

        component = "Magnitude/Phase" if index == 0 else "Real/Imaginary"

        for img in [img_1, img_2, img_3, img_4]:
            value1, value2 = img.get_component(component)
            mixing_list1.append(value1)
            mixing_list2.append(value2)

        Mix_ratios = [slider_1 / 100, slider_2 / 100, slider_3 / 100, slider_4 / 100]

        for i in range(4):
            if list_combo_box[i] == 0:  # Magnitude or Real
                newmag += Mix_ratios[i] * mixing_list1[i]
                newreal += Mix_ratios[i] * mixing_list1[i]
            else:  # Phase or Imaginary
                newphase += Mix_ratios[i] * mixing_list2[i]
                newimag += Mix_ratios[i] * mixing_list2[i]

        if index == 0:
            new_mixed_ft = np.multiply(newmag, np.exp(1j * newphase))
        else:
            new_mixed_ft = newreal + 1j * newimag

        return ImageDisplay.inverse_fourier(new_mixed_ft)
    
    def inverse_fourier(newimage):
        Inverse_fourier_image = np.real(np.fft.ifft2(np.fft.ifftshift(newimage)))
        return Inverse_fourier_image