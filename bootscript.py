import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from time import sleep
import subprocess

from scapy.all import *
from time import sleep



# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)


interface = "wlan1"

#rssicommand = str('cat /proc/net/wireless | cut -d " " -f7') #| cut -d " " -f7')
#rssicommand = str('echo test')

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

draw = ImageDraw.Draw(image)
#textbox = ImageDraw.Draw(image)

#Font
fnt = ImageFont.load_default()

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)


#load images
Menuimage = Image.open("/home/me/Menuimage.bmp").convert("1")
Menuimage_meow = Image.open("/home/me/Menuimage_meow.bmp").convert("1")
Menuimage_hiss = Image.open("/home/me/Menuimage_hiss.bmp").convert("1")
Tool1image = Image.open("/home/me/Tool1image.bmp").convert("1")
Infoimage = Image.open("/home/me/Infoimage.bmp").convert("1")
ToolLimage = Image.open("/home/me/ToolLimage.bmp").convert("1")
ToolRimage = Image.open("/home/me/ToolRimage.bmp").convert("1")


#wifi scanner variables
apMAC = ""      #Access point MAC address
sourceMAC = ""  #Sender MAC address
destMAC = ""    #Reciever MAC address
rssi = ""       #Access point Signal strength
ap = ""         #Access point name/SSID

#Put filtering values here (yet to be fully tested lmao)
#-------------------
filterSSID = False
targetSSID = False
filterMAC = ""
targetMAC = ""
#-------------------

#_____________________________________________________________________________________		Functions

def text_output(text):
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	disp.show()
	#draw.text((5, 5), "rssi here", font=fnt)
	#draw.text((5, 5), "test", fill=255)
	draw.multiline_text((5, 5), text, fill=255)
	disp.image(image)
	disp.show()
	return

def rssi_value():
    #Get and return the RSSI of nearby devices
    #string rssi_output = os.system(""sudo iw wlo1 scan | awk "/signal:/ || /SSID:/"").decode()
    rssi_scan = subprocess.run(rssicommand, shell=True, capture_output=True, text=True)
    rssi_output = rssi_scan.stdout

    return rssi_output

#collect wifi packet and filter
def wifi_scanner_getpacket():
	pkt = sniff(iface = interface, count=1)[0]

	#if no wifi protocol layer detected, skip
	if not pkt.haslayer(Dot11):
		text_output("No packet found") #
		#reset variables
		apMAC = ""      #Access point MAC address
		sourceMAC = ""  #Sender MAC address
		destMAC = ""    #Reciever MAC address
		rssi = ""       #Access point Signal strength
		ap = ""         #Access point name/SSID
		return

    	#Check if it has a wifi beacon or probe response layer, then save SSID
	if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
		ap = pkt[Dot11Elt].info.decode(errors="ignore")
		if ap == "":
			ap = "<BROARDCAST>"
	else:
		ap = "no beacon"

   	#Check if it has a RadioTap layer, then save RSSI
	if pkt.haslayer(RadioTap):
		rssi = pkt.dBm_AntSignal

    	#Check if it has the wifi layer, then save source, dest and ap mac addresses
	if pkt.haslayer(Dot11):
		destMAC = pkt[Dot11].addr1
		sourceMAC = pkt[Dot11].addr2
		apMAC = pkt[Dot11].addr3

	#Scuffed IF filter (should be swapped to a switch case)
	#Check if there is an SSID filter
	if filterSSID == True:
		#If so, Check if packet matches filter
		if ap == targetSSID:
			#If so, is there a MAC filter?
			if filterMAC == True:
				#If so, does packet match filter?
				if sourceMAC == targetMAC:
					#If so, print packet
					wifi_output(ap, apMAC, sourceMAC, destMAC)
			#If no MAC Filter, Print with just matching SSID
			else:
				wifi_output(ap, apMAC, sourceMAC, destMAC)
	#If just MAC Filter is chosen
	elif (filterSSID == False) & (filterMAC == True):
		if sourceMAC == targetMAC:
	            	#If so, print packet
			wifi_output(ap, apMAC, sourceMAC, destMAC)
    	#If neither filter, Print any packet
	else:
		wifi_output(ap, apMAC, sourceMAC, destMAC)
	return


#Print out feild details if they are there
def wifi_output(ap, apMAC, sourceMAC, destMAC):

	if (apMAC is None):
		apMAC = " -null- "

	if (sourceMAC is None):
		sourceMAC = " -null- "

	if (destMAC is None):
		destMAC = " -null- "

    	#Print packet SSID and ap MAC Address
    	#Print MAC address traffic of packet
	wifiOutput = str(ap + "\n[" + apMAC + "]:\n" + sourceMAC + " ->\n-> " + destMAC)

	text_output(wifiOutput)

	#Could instead have values saved to SQL database here.
	return



def wifi_scanner():
#	# Clear display.
	disp.fill(0)
	disp.show()
	while button_B.value:
        #Run packet scanner until B button is pressed

		wifi_scanner_getpacket()

	else:
#		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		disp.fill(0)
		disp.show
		return


def rssi_reader():
    # Clear display.
	disp.fill(0)
	disp.show()
	while button_B.value:
        #Run RSSI scanner until B button is pressed
		text_output("AP:RSSI")

	else:
#		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		disp.fill(0)
		disp.show
		return

#-------------------------------------------------------------------------------







def screen_test():
	draw.line((0, 0) + image.size, fill=128)
	draw.line((0, image.size[1], image.size[0], 0), fill=25)

def A_button_pressed():
	draw.polygon([(0, 0), (10, 0), (0, 10)], outline=128, fill=1)
	time.sleep(1)
	draw.polygon([(0, 0), (15, 0), (0, 15)], outline=128, fill=1)
	time.sleep(1)
	draw.polygon([(0, 0), (20, 0), (0, 20)], outline=128, fill=1)
	time.sleep(1)
    
def LEFT_menu():
    # Clear display
    disp.fill(0)
    disp.show()

    while not button_L.value:
        disp.image(ToolLimage)
        disp.show()
        
        if not button_A.value:
            wifi_scanner()

def RIGHT_menu():
    # Clear display
    disp.fill(0)
    disp.show()

    while not button_R.value:
        disp.image(ToolRimage)
        disp.show()
        
        if not button_A.value:
            rssi_reader()

def UP_menu():
#	# Clear display.
	disp.fill(0)
	disp.show()
	while not button_U.value:
		#draw.rectangle((0, 0, width, height), outline=255, fill=1)
		#draw.polygon([(0, 0), (20, 20), (40, 0)], outline=128, fill=0)
		disp.image(Tool1image)
		#if not button_A.value:
			#draw.ellipse((70, 40,90, 60), outline=255, fill=0)
			#call function
		#disp.image(image)
		disp.show()
	else:
#		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		disp.fill(0)
		disp.show
		return



def DOWN_menu():
#	# Clear display.
	disp.fill(0)
	disp.show()
	while not button_D.value:
		#draw.rectangle((0, 0, width, height), outline=255, fill=1)
		#draw.polygon([(0, 64), (20, 44), (40, 64)], outline=128, fill=0)
		disp.image(Infoimage)
		#if not button_A.value:
			#draw.ellipse((70, 40, 90, 60), outline=128, fill=0)
			#call function
		#disp.image(image)
		disp.show()
	else:
#		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		disp.fill(0)
		disp.show()
		return


#_____________________________________________________________________________________		Main Loop
while True:


    if not button_U.value:  # button is released
#        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  # Up
#    else:  # button is pressed:
        UP_menu()
        #draw.rectangle((0, 0, width, height), outline=0, fill=0)
        #draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  # Up filled

#    if button_L.value:  # button is released
#        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  # left
#    else:  # button is pressed:

        #draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  # left filled

#    if button_R.value:  # button is released
#        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0)  # right
#    else:  # button is pressed:

        #draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1)  # right filled

    if not button_D.value:  # button is released
#        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0)  # down
#    else:  # button is pressed:
        DOWN_menu()
        #draw.rectangle((0, 0, width, height), outline=0, fill=0)
        #draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1)  # down filled

#    if button_C.value:  # button is released
#        draw.rectangle((20, 22, 40, 40), outline=255, fill=0)  # center
#    else:  # button is pressed:
        #draw.rectangle((20, 22, 40, 40), outline=255, fill=1)  # center filled

    if not button_L.value:
        LEFT_menu()

    if not button_R.value:
        RIGHT_menu()

    if not button_A.value:  # button is released
        #draw.ellipse((70, 40, 90, 60), outline=255, fill=0)  # A button
        disp.image(Menuimage_hiss)
        #else:  # button is pressed:
        #A_button_pressed()  # A button filled

    elif not button_B.value:
        #draw.ellipse((100, 20, 120, 40), outline=255, fill=0)  # B button
        disp.image(Menuimage_meow)
        #else:  # button is pressed:
        #screen_test()  # B button filled
    else:
        disp.image(Menuimage)
    #disp.image(image)
    #draw.polygon([(32, 32), (64, 64), (98, 32), (64, 0)], outline=255, fill=1)
    disp.show()

#while True:
#	while not button_U.value:
#		UP_menu()
#	while not button_D.value:
#	DOWN_menu()
#	#if True: #not button_U.value and not button_D.value:
#	draw.rectangle((0, 0, width, height), outline=0, fill=0)
#disp.show()
