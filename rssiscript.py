#! /usr/bin/env python3
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from time import sleep
import subprocessxz

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

rssicommand = str('sudo iw wlo1 scan | awk "/signal:/ || /SSID:/"')

# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP


# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
textbox = ImageDraw.Draw(out)
draw = ImageDraw.Draw(image)


#Font
fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)


#load images
Menuimage = Image.open("/home/me/Menuimage.bmp").convert("1")
Menuimage_meow = Image.open("/home/me/Menuimage_meow.bmp").convert("1")
Menuimage_hiss = Image.open("/home/me/Menuimage_hiss.bmp").convert("1")
Tool1image = Image.open("/home/me/Tool1image.bmp").convert("1")
Infoimage = Image.open("/home/me/Infoimage.bmp").convert("1")
ToolLimage = Image.open("/home/me/ToolLimage").convert("1")

#_____________________________________________________________________________________		Functions

def rssi_value():
    #Get and return the RSSI of nearby devices
    #string rssi_output = os.system(""sudo iw wlo1 scan | awk "/signal:/ || /SSID:/"").decode()
    rssi_scan = subprocess.run(rssicommand, shell=True, capture_output=True, text=True)
    rssi_output = rssi_scan.stdout

    return rssi_output

def rssi_read():
#	# Clear display.
	disp.fill(0)
	disp.show()
	while button_B.value:
        #Run RSSI scanner until B button is pressed
        #rssi_value()
        
		textbox.multiline_text((10, 10), rssi_value(), font=fnt, fill=(0, 0, 0))
		disp.show()
	else:
#		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		disp.fill(0)
		disp.show
		return    

def screen_test():
	draw.line((0, 0) + image.size, fill=128)
	draw.line((0, image.size[1], image.size[0], 0), fill=25)
#___________________________________________________________________________________		Main Loop

while(True):
    rssi_read()




