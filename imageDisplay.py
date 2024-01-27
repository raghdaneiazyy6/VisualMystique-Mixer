# image_display.py

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QDateTime
import cv2
import numpy as np
from itertools import permutations
from collections import Counter

class ImageDisplay:
    
    def __init__(self, label, image_component,combo_box= None,label_combination = None,out_combo_box = None,label_out_1=None, label_out_2=None):
        self.label = label
        self.last_click_time = 0
        self.image_component = image_component
        self.combo_box = combo_box
        self.label_combination = label_combination
        self.out_combo_box = out_combo_box
        self.label_out_1 = label_out_1
        self.label_out_2 = label_out_2

        if self.combo_box is not None:
            self.combo_box.currentIndexChanged.connect(self.handle_combobox_change)

    def on_label_double_clicked(self, event):
        current_time = QDateTime.currentMSecsSinceEpoch()
        if current_time - self.last_click_time < 500:
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
        self.original_image = cv2.imdecode(np.frombuffer(open(self.image_path, 'rb').read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        resized_image = cv2.resize(self.original_image, (1500, 500), interpolation=cv2.INTER_AREA)
        height, width = resized_image.shape
        bytes_per_line = width
        q_image = QImage(resized_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.label.size(), aspectRatioMode=Qt.KeepAspectRatio)
        self.label.setPixmap(scaled_pixmap)
        self.ft = np.fft.fft2(self.original_image)
        fourier_shift = np.fft.fftshift(self.ft)
        magnitude = np.multiply(np.log10(1 + np.abs(fourier_shift)), 20)
        
        
        self.set_magnitude_image(magnitude)

    def set_magnitude_image(self, magnitude_image):
        resized_magnitude = cv2.resize(magnitude_image, (1500, 500), interpolation=cv2.INTER_AREA)

        # Convert resized NumPy array to bytes
        resized_magnitude_bytes = resized_magnitude.astype(np.uint8).tobytes()

        height, width = resized_magnitude.shape
        bytes_per_line = width
        q_image = QImage(resized_magnitude_bytes, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.image_component.size(), aspectRatioMode=Qt.KeepAspectRatio)
        self.image_component.setPixmap(scaled_pixmap)

    def handle_combobox_change(self):
        if self.combo_box is not None:
            selected_index = self.combo_box.currentIndex()
            self.set_transformed_image_by_index(selected_index)

    def set_transformed_image_by_index(self, index):
        fourier_shift = np.fft.fftshift(self.ft)
        if index == 0:  # Magnitude
            transformed_image = np.multiply(np.log10(1 + np.abs(fourier_shift)), 20)
        elif index == 1:  # Phase
            transformed_image = np.angle(fourier_shift)
        elif index == 2:  # Real
            transformed_image = np.real(fourier_shift)
        elif index == 3:  # Imaginary
            transformed_image = np.imag(fourier_shift)
        else:      # Magnitude
            transformed_image = np.multiply(np.log10(1 + np.abs(fourier_shift)), 20)

        resized_transformed = cv2.resize(transformed_image, (1500, 500), interpolation=cv2.INTER_AREA)
        # Convert resized NumPy array to bytes
        resized_transformed_bytes = resized_transformed.astype(np.uint8).tobytes()
        height, width = resized_transformed.shape
        bytes_per_line = width
        q_image = QImage(resized_transformed_bytes, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.image_component.size(), aspectRatioMode=Qt.KeepAspectRatio)
        self.image_component.setPixmap(scaled_pixmap)

    def get_component(self, component):
        
        if self.ft is None:
            
            return None , None
        
        fourier_shift = np.fft.fftshift(self.ft)
        
        if component== "Magnitude/Phase"  :  # Magnitude
            
            return  np.abs(fourier_shift) , np.angle(fourier_shift)
        elif component== "Real/Imaginary":  # Real
            return np.real(fourier_shift),np.imag(fourier_shift)

    def combination ( img_1, img_2, img_3, img_4, index,
                                      slider_1, slider_2, slider_3, slider_4):
        
        mixing_list1 = []
        mixing_list2 = []
        if index == 0:
            component = "Magnitude/Phase"
        else:
            component = "Real/Imaginary"

        
        newValue ,newValue2 =img_1.get_component(component)
        newValue3 ,newValue4 =img_2.get_component(component)
        newValue5 ,newValue6 =img_3.get_component(component)
        newValue7 ,newValue8 =img_4.get_component(component)
        mixing_list1.extend([newValue, newValue3, newValue5, newValue7])
        mixing_list2.extend([newValue2, newValue4, newValue6, newValue8])

        Mix_ratio_1 = slider_1 / 100
        Mix_ratio_2 = slider_2 / 100
        Mix_ratio_3 = slider_3 / 100
        Mix_ratio_4 = slider_4 / 100
        
        if index ==0 :
            

            newmag = Mix_ratio_1 * mixing_list1[0] + Mix_ratio_2 * mixing_list1[1] + Mix_ratio_3 * mixing_list1[
                2] + Mix_ratio_4 * mixing_list1[3]
            
            newphase = Mix_ratio_1 * mixing_list2[0] + Mix_ratio_2 * mixing_list2[1] + Mix_ratio_3 * mixing_list2[
                2] + Mix_ratio_4 * mixing_list2[3]
            new_mixed_ft = np.multiply(newmag, np.exp(1j *newphase))
        else:
            
            newreal =Mix_ratio_1 * mixing_list1[0] + Mix_ratio_2 * mixing_list1[1] + Mix_ratio_3 * mixing_list1[
                2] + Mix_ratio_4 * mixing_list1[3]
            
            newimag = Mix_ratio_1 * mixing_list1[0] + Mix_ratio_2 * mixing_list1[1] + Mix_ratio_3 * mixing_list1[
                2] + Mix_ratio_4 * mixing_list1[3]
            new_mixed_ft = newreal + 1j * newimag

        return ImageDisplay.inverse_fourier(new_mixed_ft)
    
    def inverse_fourier(newimage):
        
        Inverse_fourier_image = np.real(np.fft.ifft2(np.fft.ifftshift(newimage)))
        
        # return Inverse_fourier_image
        return Inverse_fourier_image
