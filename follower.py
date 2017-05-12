import serial
import RPi.GPIO as GPIO
import time

def readSensor(_ser):
	_ser.flushInput()
	_ser.readline()
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
	global ml
	global mr
	if isNumeric(speed):
		speed = speed if speed<100 else 100
		speed = speed if speed>0 else 0
		if lr=="r":
			mr.ChangeDutyCycle(speed)
		elif lr=="l":
			ml.ChangeDutyCycle(speed)

def pt_right():
	global turn_bias
	global lspeed_bias
	global rspeed_bias
	setMotorSpeed("l",50*lspeed_bias);
	setMotorSpeed("r",50*rspeed_bias);	
	setMotor("l",'F')
	setMotor("r",'R')
	time.sleep(0.05 * turn_bias)
	setMotor("l",'F')
	setMotor("r",'F')
	setMotorSpeed("l",90*lspeed_bias);
	setMotorSpeed("r",90*rspeed_bias);	

def pt_left():
	global turn_bias
	global lspeed_bias
	global rspeed_bias	
	setMotorSpeed("l",50*lspeed_bias);
	setMotorSpeed("r",50*rspeed_bias);	
	setMotor("l",'R')
	setMotor("r",'F')
	time.sleep(0.05 * turn_bias)
	setMotor("l",'F')
	setMotor("r",'F')
	setMotorSpeed("l",90*lspeed_bias);
	setMotorSpeed("r",90*rspeed_bias);	

def straight_a_bit(dist):
	global speed_bias
	global lspeed_bias
	global rspeed_bias	
	setMotorSpeed("l",90*lspeed_bias);
	setMotorSpeed("r",90*rspeed_bias);		
	setMotor("l",'F')
	setMotor("r",'F')
	time.sleep(0.01 * dist / speed_bias)
	setMotor("l",'F')
	setMotor("r",'F')

mr,ml = initMotor()
ser = initSensor()

delta = 0
heading = 0
target_heading = 0
thl = [450,400,390,340,290]

dist_bias = 0
turn_bias = 35
lspeed_bias = 0.9
rspeed_bias = 0.9
speed_bias = (lspeed_bias + rspeed_bias) / 2

try:
	setMotor("l",'F')
	setMotor("r",'F')

	while True:
		th = list(map(lambda x: x + dist_bias,thl))
		IRH,IRF,IRB = readSensor(ser)
		heading = IRF-IRB
		lspeed_bias, rspeed_bias = 0.9, 0.9

		print "target heading: {}".format(target_heading)
		print "IRH: {} IRF: {} IRB: {}".format(IRH,IRF,IRB)
		
		if IRH > 300 :
			pt_right()
			target_heading = 0

		if IRF < 200 :
			straight_a_bit(70)
			pt_left()
			straight_a_bit(170)
		elif IRF < th[4]:
			target_heading = 80
			lspeed_bias, rspeed_bias = 0.5, 0.5
		elif IRF < th[3]:
			target_heading = 80
			lspeed_bias, rspeed_bias = 0.5, 0.5
		elif IRF < th[2]:
			target_heading = 50
			lspeed_bias, rspeed_bias = 0.7, 0.7
		elif IRF < th[1]:
			target_heading = 0
			lspeed_bias, rspeed_bias = 0.9, 0.9
		elif IRF < th[0]:
			target_heading = -50
			lspeed_bias, rspeed_bias = 0.7, 0.7
			delta = IRF - th[1]
		else:
			target_heading = -80
			lspeed_bias, rspeed_bias = 0.5, 0.5
		
		if heading - target_heading > 0 :
			setMotorSpeed("l",90*lspeed_bias);
			setMotorSpeed("r",(90-(heading - target_heading)/4.4)*rspeed_bias);

		if heading - target_heading < 0 :
			setMotorSpeed("l",(90+(heading - target_heading)/4.4)*lspeed_bias);
			setMotorSpeed("r",90*rspeed_bias);
finally:
    ml.stop()
    mr.stop()
    GPIO.cleanup()
