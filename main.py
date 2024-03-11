import sys
from os import path
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QApplication
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from ImageDisplay import ImageDisplay
import logging
logging.basicConfig(filename='user.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "design.ui"))

class MainApp(QMainWindow, FORM_CLASS):

    def __init__(self, parent=None):
        super().__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Image Mixer")

        for slider in [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4]:   #refactored
            slider.valueChanged.connect(self.on_changed)

        for combo_box in [self.comboBox_1, self.comboBox_2, self.comboBox_3, self.comboBox_4]:       #refactored
            combo_box.currentIndexChanged.connect(self.on_changed)

        self.combobox_list = [self.comboBox_1,self.comboBox_2,self.comboBox_3,self.comboBox_4]
        self.combobox_list_index= [self.comboBox_1.currentIndex(),self.comboBox_2.currentIndex(),self.comboBox_3.currentIndex(),self.comboBox_4.currentIndex()]

        for slider in [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4]: #refactored
            slider.setValue(0)

        for button in [self.insideButton_1, self.insideButton_2, self.insideButton_3, self.insideButton_4]:
            button.setChecked(True)
        
        self.newimage = None
        # Create instances of ImageDisplay for each label
        self.image_display1 = ImageDisplay(self.imageLabel1, self.imageComponent1, self.imageComboBox1, self.comboBox_5, self.insideButton_1, 0)
        self.image_display2 = ImageDisplay(self.imageLabel2, self.imageComponent2, self.imageComboBox2, self.comboBox_5, self.insideButton_2, 0)
        self.image_display3 = ImageDisplay(self.imageLabel3, self.imageComponent3, self.imageComboBox3, self.comboBox_5, self.insideButton_3, -1)
        self.image_display4 = ImageDisplay(self.imageLabel4, self.imageComponent4, self.imageComboBox4, self.comboBox_5, self.insideButton_4, 0)

        self.progressBar.setValue(0)  # Set initial value of the progress bar

        for label, image_display in zip([self.imageLabel1, self.imageLabel2, self.imageLabel3, self.imageLabel4], [self.image_display1, self.image_display2, self.image_display3, self.image_display4]):
            label.mouseDoubleClickEvent = image_display.on_label_double_clicked

        for combo_box, image_display in zip([self.imageComboBox1, self.imageComboBox2, self.imageComboBox3, self.imageComboBox4], [self.image_display1, self.image_display2, self.image_display3, self.image_display4]):
            combo_box.currentIndexChanged.connect(image_display.handle_combobox_change)

        for radiobutton, image_display in zip([self.insideButton_1, self.insideButton_2, self.insideButton_3, self.insideButton_4], [self.image_display1, self.image_display2, self.image_display3, self.image_display4]):
            radiobutton.toggled.connect(image_display.ExtractRegion)
            radiobutton.toggled.connect(self.on_changed)

        for radiobutton, image_display in zip([self.outsideButton_1, self.outsideButton_2, self.outsideButton_3, self.outsideButton_4], [self.image_display1, self.image_display2, self.image_display3, self.image_display4]):
            radiobutton.toggled.connect(image_display.ExtractRegion)
            radiobutton.toggled.connect(self.on_changed)

        # Connect the combination signal to the combination function
        self.radioButton1.setChecked(True)
        self.radioButton1.toggled.connect(self.on_changed)
        self.pushButton.clicked.connect(self.start_progress)
        self.pushButton_2.clicked.connect(self.cancel_operation)
        self.verticalSlider.valueChanged.connect(self.updateRectangle)

    def start_progress(self):
        self.progressBar.setValue(0)  # Set initial value of the progress bar
        # Create a QTimer to simulate progress updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(12)  # Adjust the interval (in milliseconds) as needed

    def update_progress(self):
        # Update the progress bar value
        current_value = self.progressBar.value()
        if current_value < 100:
            self.progressBar.setValue(current_value + 1)  # Increment the progress value
        else:
            self.timer.stop()
            self.press_Apply(self.newimage)
            # Stop the timer when the progress reaches 100%

    def cancel_operation(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()  # Stop the timer if it is active
        self.progressBar.setValue(0)

    def press_Apply(self,newimage):
        index = self.comboBox_5.currentIndex()
        if index == 0:
            logging.info(f'Output image will be displayed in output #1')
        else: 
            logging.info(f'Output image will be displayed in output #2')
        newimage = cv2.add(newimage, 50)
        resized_image = cv2.resize(newimage, (self.outputImage1.width(), self.outputImage1.height()), interpolation=cv2.INTER_AREA)
        height, width = resized_image.shape
        bytes_per_line = width
        q_image = QImage(resized_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        scene = QGraphicsScene()
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
        scene.addItem(pixmap_item)
        logging.info('Rectangle size updated successfully.')
        logging.info('Output image is displayed.')

        if index==0 :
            self.outputImage1.setScene(scene)
            self.outputImage1.fitInView(pixmap_item, Qt.KeepAspectRatio)
        else:
            self.outputImage2.setScene(scene)
            self.outputImage2.fitInView(pixmap_item, Qt.KeepAspectRatio)

    def on_changed(self):
        slider_values = [self.verticalSlider_1.value(), self.verticalSlider_2.value(), self.verticalSlider_3.value(), self.verticalSlider_4.value()]
        if self.radioButton1.isChecked():
            index = 0
            component_labels = ["Magnitude", "Phase"]
            logging.info(f'Magnitude/Phase mode selected')
        else:
            index = 1
            component_labels = ["Real", "Imaginary"]
            logging.info(f'Real/Imaginary mode selected')
        
        for i, (slider_value, combo_box) in enumerate(zip(slider_values, self.combobox_list)):
            if combo_box.currentIndex() == 0:
                logging.info(f'Slider {i + 1} value: {slider_value}, Manipulated image: {i + 1}, Component: {component_labels[0]}')
            else:
                logging.info(f'Slider {i + 1} value: {slider_value}, Manipulated image: {i + 1}, Component: {component_labels[1]}')

        for i, combo_box in enumerate(self.combobox_list):
            combo_box.setItemText(0, component_labels[0])
            combo_box.setItemText(1, component_labels[1])

        indexes = [combo_box.currentIndex() for combo_box in [self.comboBox_1, self.comboBox_2, self.comboBox_3, self.comboBox_4]]
        if self.imageLabel4.scene() is not None :
            self.newimage = ImageDisplay.combination(self.image_display1, self.image_display2, self.image_display3, self.image_display4, index, *slider_values, indexes)
            self.newimage = cv2.normalize(self.newimage, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            self.newimage  = self.newimage .astype('uint8')

    def updateRectangle(self):
        max_width = self.imageComponent1.width()
        max_height = self.imageComponent1.height()
        self.verticalSlider.setMaximum(max_width)
        value = self.verticalSlider.value()
        if(value >= max_height):
            self.image_display1.update_rect_size(value, max_height)
            self.image_display2.update_rect_size(value, max_height)
            self.image_display3.update_rect_size(value, max_height)
            self.image_display4.update_rect_size(value, max_height)
        else:
            self.image_display1.update_rect_size(value, value)
            self.image_display2.update_rect_size(value, value)
            self.image_display3.update_rect_size(value, value)
            self.image_display4.update_rect_size(value, value)

        self.on_changed()
    

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
