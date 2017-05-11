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

def isNumeric(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False    

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

def setMotor(lr, cmd):
    FWD1 = False if lr=="r" else True
    FWD2 = True if lr=="r" else False
    in1 = 2 if lr=="r" else 5
    in2 = 3 if lr=="r" else 6
    if cmd == 'F':
        GPIO.output(in1, FWD1)
        GPIO.output(in2, FWD2)
    elif cmd == 'R':
        GPIO.output(in1, FWD2)
        GPIO.output(in2, FWD1)    
    elif cmd == 'S':
        GPIO.output(in1, False)
        GPIO.output(in2, False) 

def setMotorSpeed(lr, speed):
	if isNumeric(speed):
		if lr=="r":
			p0.ChangeDutyCycle(speed)
		elif lr=="l":
			p1.ChangeDutyCycle(speed)

def pt_right():
	global turn_bias
	setMotor("l",'F')
	setMotor("r",'R')
	time.sleep(0.05 * turn_bias)
	setMotor("l",'S')
	setMotor("r",'S')

def pt_left():
	global turn_bias
	setMotor("l",'R')
	setMotor("r",'F')
	time.sleep(0.05 * turn_bias)
	setMotor("l",'S')
	setMotor("r",'S')

def straight_a_bit(dist):
	global speed_bias
	setMotor("l",'F')
	setMotor("r",'F')
	time.sleep(0.01 * dist / speed_bias)
	setMotor("l",'S')
	setMotor("r",'S')

ml,mr = initMotor()
ser = initSensor()

delta = 0
heading = 0
target_heading = 0
thl = [450,400,390,340,290]

dist_bias = 0
turn_bias = 10
speed_bias = 0.9

while True:
	th = list(map(lambda x: x + dist_bias,thl))
	IRH,IRF,IRB = readSensor(ser)
	heading = IRF-IRB
	
	if IRH > 300 :
		pt_right()
		target_heading = 0

	if IRF < 200 :
		straight_a_bit(88)
		pt_left()
		straight_a_bit(130)
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
		setMotorSpeed("l",90*speed_bias);
		setMotorSpeed("r",(90-(heading - target_heading)/90.0)*speed_bias);

	if heading - target_heading < 0 :
		setMotorSpeed("l",(90+(heading - target_heading)/90.0)*speed_bias);
		setMotorSpeed("r",90*speed_bias);




		