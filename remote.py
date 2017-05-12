import serial
import RPi.GPIO as GPIO
import time
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

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
	setMotorSpeed("l",90);
	setMotorSpeed("r",90);
	setMotor("l",'F')
	setMotor("r",'R')
	time.sleep(0.2)
	setMotor("l",'S')
	setMotor("r",'S')

def pt_left():
	setMotorSpeed("l",90);
	setMotorSpeed("r",90);	
	setMotor("l",'R')
	setMotor("r",'F')
	time.sleep(0.2)
	setMotor("l",'S')
	setMotor("r",'S')

def straight_a_bit():
	setMotorSpeed("l",90);
	setMotorSpeed("r",90);		
	setMotor("l",'F')
	setMotor("r",'F')
	time.sleep(0.2)
	setMotor("l",'S')
	setMotor("r",'S')

def bstraight_a_bit():
	setMotorSpeed("l",90);
	setMotorSpeed("r",90);		
	setMotor("l",'R')
	setMotor("r",'R')
	time.sleep(0.2)
	setMotor("l",'S')
	setMotor("r",'S')

mr,ml = initMotor()
ser = initSensor()


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        if "rt" in post_data:
        	pt_right()
        elif "lt" in post_data:
        	pt_left()
        elif "ff" in post_data:
        	straight_a_bit()
        elif "rr" in post_data:
        	bstraight_a_bit()
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
		run()