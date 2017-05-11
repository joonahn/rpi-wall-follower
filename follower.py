import serial
import RPi.GPIO as GPIO
import time

def readSensor(_ser):
	raw_data = _ser.readline()
	data = raw_data.split('\t')
	if len(data)<3:
		return 0,0,0 # Error
	else:
		data = list(map(lambda x: x.strip(),data))
		val = list(map(lambda x: int(x), data))
		return val[0],val[1],val[2]

def initSensor():
	_ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
	_ser.readline() # Flush initial data
	return _ser


def initMotor():
	pwm0 = 18
	pwm1 = 13
	ain1 = 2
	ain2 = 3
	bin1 = 5
	bin2 = 6

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pwm0, GPIO.OUT)
	GPIO.setup(pwm1, GPIO.OUT)
	GPIO.setup(ain1, GPIO.OUT)
	GPIO.setup(ain2, GPIO.OUT)
	GPIO.setup(bin1, GPIO.OUT)
	GPIO.setup(bin2, GPIO.OUT)

	GPIO.output(ain1, False)
	GPIO.output(ain2, True)
	GPIO.output(bin1, True)
	GPIO.output(bin2, False)

	p0 = GPIO.PWM(pwm0, 50)
	p0.start(50)
	p0.ChangeDutyCycle(0)
	p0.ChangeFrequency(50)

	p1 = GPIO.PWM(pwm1, 50)
	p1.start(50)
	p1.ChangeDutyCycle(0)
	p1.ChangeFrequency(50)
	return p0,p1

ml,mr = initMotor()
ser = initSensor()

delta = 0
heading = 0
target_heading = 0

dist_bias = 0
turn_bias = 0
speed_bias = 0

while True:
	thl = [450,400,390,340,290]
	th = list(map(lambda x: x + dist_bias,thl))
	IRH,IRF,IRB = readSensor(ser)
	heading = IRF-IRB
	
	if IRH > 300 :
		pt_right()
		target_heading = 0

	if IRF < 200 :
		straight_a_bit()
		pt_left()
		straight_a_bit()
	elif IRF < th5:
		target_heading = 80
	elif IRF < th4:
		target_heading = 80
	elif IRF < th3:
		target_heading = 50
	elif IRF < th2:
		target_heading = 0
	elif IRF < th1:
		target_heading = -50
		delta = IRF - th2
	else:
		target_heading = -80
	
	if heading - target_heading > 0 :
		




		
