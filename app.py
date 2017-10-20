# import library
from os import path, remove
from datetime import datetime
import sys, requests, uuid, getopt
import spidev
from picamera import PiCamera

# open SPI interface
spi = spidev.SpiDev()
spi.open(0,0)
# define the sensor channel
ax_ch = 0
ay_ch = 1
az_ch = 2
light_ch = 3
temp_ch  = 4
volts_ch = 5
# Resistive divider resistor set
v_r1 = 1000
v_r2 = 1000
# get timestamp (YYYYmmddHHMMSSssss)
ts = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')
# set capture photo name
fn = 'photo.jpg'
# application helper
def usage():
    print("Usage: %s [-h | -u ] [--help | --url=<service url, example http://192.168.0.1'>] args..."%sys.argv[0]);
# get MAC address
def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac
# read MCP3008 output (0~1023)
def ReadADC(ch):
    if ((ch > 7) or (ch < 0)):
       return -1
    adc = spi.xfer2([1,(8+ch)<<4,0])
    data = ((adc[1]&3)<<8) + adc[2]
    return data
# singal to volts
def ReadVolts(data,deci):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,deci)
    return volts
# LM35 volts to tempature
def ConvertTemp(data,deci):
    temp = data * 100
    temp = round(temp,deci)
    return temp
# solar actual volts
def ReadActVolts(data,deci):
    volts = (data * (v_r1 + v_r2) / v_r2)
    volts = round(volts,deci)
    return volts
# get environment sensor data
def GetEnvData():
    # Read the 3-Axis
    ax_data = ReadADC(ax_ch)
    ay_data = ReadADC(ay_ch)
    az_data = ReadADC(az_ch)
    # Read the photocell
    light_data = ReadADC(light_ch)
    # Read the LM35 and conversion to tempature
    temp_data = ReadADC(temp_ch)
    temp_volts = ReadVolts(temp_data,4)
    temp = ConvertTemp(temp_volts,2)
    # Read the Volts
    volts_data = ReadADC(volts_ch)
    volts = ReadVolts(volts_data,4)
    act_volts = ReadActVolts(volts,4)
    # transform to json format
    data = {
        'ts': ts,
        'ax': ax_data,
        'ay': ay_data,
        'az': az_data,
        'light': light_data,
        'temp': temp,        
        'volts': act_volts
    }
    return data

# photo capture
def Capture(name):
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.capture(name)

def main():
    try:
        # get args
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["help", "url="])
        if len(opts) == 0:
            print ("Please input correct args...")
            usage()
            sys.exit(1)
        for opt, arg in opts:            
            if opt in ("-h", "--help"):
                usage()
                sys.exit(1)
            elif opt in ("-u", "--url"):
                url = arg

    except getopt.GetoptError:
        print ("Get args error..")
        usage()
        sys.exit(1)

    # get mac for uid
    uid = get_mac_address()

    # upload sensor data
    
    # use POST method to upload data
    data = GetEnvData()
    r = requests.post(url+'/addenvdata/%s'%uid, json=data)
    print(r)

    # upload photo
    # remove photo.jpg
    if path.exists(fn):
        remove(fn)
    # capture photo
    Capture(fn)
    # open photo
    f = {'file': open(fn,'rb')}
    # use POST method to upload photo
    r = requests.post(url+'/uploader/%s'%uid, files=f)
    print(r)

if __name__ == "__main__":
   main()