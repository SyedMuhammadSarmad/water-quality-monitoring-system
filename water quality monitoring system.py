import machine
import urequests 
from machine import Pin,ADC
import time, network
import dht
import network

sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.scan()                             # Scan for available access points
sta_if.connect("YOUR WIFI NAME", "YOUR WIFI PASSWORD") # Connect to an AP
while 1:
    val=sta_if.isconnected()
    if val:
        print("connectd")
        break
#pH code pin
SensorPin = 35  # Replace with the correct ADC pin you're using
adc_ph = ADC(Pin(SensorPin))

#Tds pin
adc_pin_tds = 32  # Change this to the correct ADC pin you're using
adc_tds = ADC(Pin(adc_pin_tds))
adc_tds.atten(ADC.ATTN_11DB)  # Set the attenuation to match the input voltage range

#Turbidity Pin
adc_pin_turb = 33  # Change this to the correct ADC pin you're using
adc_turb = ADC(Pin(adc_pin_turb))
adc_turb.atten(ADC.ATTN_11DB)  # Set the attenuation to match the input voltage range



def analog_to_turbidity(analog_value):
    # Convert analog value to turbidity using your calibration formula
    # You need to calibrate this conversion based on your specific sensor
    # Consult your sensor's datasheet or documentation for guidance
    analog_min = 1932  # Minimum analog value corresponding to pH 0 #100
    analog_max = 0 # Maximum analog value corresponding to pH 14 #3000
    
    turb_min=15
    turb_max=50
    turbidity_value = turb_min + (analog_value - analog_min) * (turb_max - turb_min) / (analog_max - analog_min)
    return round(turbidity_value,2)

def analog_to_tds(analog_value):
    # Convert analog value to TDS using your calibration formula
    # You need to calibrate this conversion based on your specific sensor
    # Consult your sensor's datasheet or documentation for guidance
    analog_min = 0  
    analog_max = 1778
    
    tds_min = 700 # pH value corresponding to analog_min
    tds_max = 0  # pH value corresponding to analog_max
    
    tds_value = tds_min + (analog_value - analog_min) * (tds_max - tds_min) / (analog_max - analog_min)
    
#     print("Calculated pH:", tds_value)
    return tds_value

def read_ph_value():
    buf = [0] * 10
    for i in range(10):
        buf[i] = adc_ph.read()
        time.sleep(0.01)
    
    buf.sort()
    avg_value = sum(buf[2:8]) / 6
    
    ph_value = (avg_value * 5.0 / 1023 / 5) * 3.3
    
    return round(ph_value,1)


HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = 'YOUR API KEY' 

UPDATE_TIME_INTERVAL = 5000  # in ms 
last_update = time.ticks_ms() 

# Configure ESP32 as Station
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)

print('network config:', sta_if.ifconfig()) 

while True: 
    if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL: 
        while True:
            ph_value = read_ph_value()
            
            
            analog_value_tds = adc_tds.read()
            tds_value = analog_to_tds(analog_value_tds)
            
            analog_value_turb = adc_turb.read()
            turbidity_value = analog_to_turbidity(analog_value_turb)
            
            readings = {'ph_value':ph_value,'turbidity':turbidity_value, 'tds':tds_value}
            readingscloud = {'field1':ph_value,'field2':tds_value,'field4 ':turbidity_value}
            request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY,
                                     json = readingscloud, headers = HTTP_HEADERS )  
            request.close() 
            print(readings) 