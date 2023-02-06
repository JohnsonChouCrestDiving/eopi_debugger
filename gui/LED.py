from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from .LED_widget import QLed
import time
from colorsys import rgb_to_hls, hls_to_rgb

class LED(QWidget):
    def __init__(self ,parent=None):
        super(LED, self).__init__(parent)
        self.color = QLed.Red
        self.shape = QLed.Circle
        self.value = False
        self.clickable = False
        self.brightness = 0.5
        self.status = 0
        l=QVBoxLayout(self)
        self.led=QLed(self, onColour=self.color, shape=self.shape, value=True)
        l.addWidget(self.led)

    
    def set_clickable(self):
        self.led.m_clickable = True
    
    def turn_on(self, on):
        if on:
            self.set_ok()
        else:
            self.set_error()

    def set_ok(self):
        self.value = True
        self.led.colours[2] = (0x00, 0xff, 0x00)
        self.brightness = 0.5
        return self.led.setOnColour(2)
    
    def set_error(self):
        self.value = False
        self.led.colours[1] = (0xbe, 0x01, 0x19)
        return self.led.setOnColour(1)

    def set_color(self, color):
        return self.led.setOnColour(color)
    
    def set_value(self, value):
        return self.led.setValue(value)

    def set_shape(self, shape):
        return self.led.set_shape(shape)

    def mousePressEvent(self, event):
        return self.led.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        return self.led.mouseReleaseEvent(event)
    
    def set_color_brightness(self):
        def normalise(x): return x/255.0
        def denormalise(x): return int(x*255.0)
        Red    = 1
        Green  = 2
        Yellow = 3
        Grey   = 4
        Orange = 5
        Purple = 6
        Blue   = 7

        r, g, b = self.led.colours[self.color]
        # print(r, g, b)
        h, l, s = rgb_to_hls(normalise(r),normalise(g),normalise(b))
        nr, ng, nb = hls_to_rgb(h,self.brightness,s)
        # print(denormalise(nr),denormalise(ng),denormalise(nb))  

        self.led.colours[self.color] = (denormalise(nr),denormalise(ng),denormalise(nb))

        self.set_color(self.color)
    
    

