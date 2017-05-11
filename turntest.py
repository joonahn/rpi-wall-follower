import RPi.GPIO as GPIO
import time

turn_bias = 0

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

def isNumeric(s):
    try: 
        int(s)
        return True
    except ValueError:
		return False

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
p0.ChangeDutyCycle(90)
p0.ChangeFrequency(50)

p1 = GPIO.PWM(pwm1, 50)
p1.start(50)
p1.ChangeDutyCycle(90)
p1.ChangeFrequency(50)

try:
	setMotor("r",'S')
	setMotor("l",'S')
	while True:
		text = raw_input("input command: ")
		if text.strip() == 'r':
			pt_right()
		if text.strip() == 'l':
			pt_left()
		if isNumeric(text.strip()):
			turn_bias = int(text.strip())
		
finally:
    p0.stop()
    p1.stop()
    GPIO.cleanup()

