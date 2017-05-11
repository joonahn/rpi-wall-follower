import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

ser.readline()
data = ser.readline()
print data.split('\t')
ser.close()
