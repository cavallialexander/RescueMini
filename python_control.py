import serial
import sixaxis
import sys, os
 
 
import time
 
 
 
sixaxis.init("/dev/input/js0")
 
# important AX-12 constants
AX_WRITE_DATA = 3
AX_READ_DATA = 4
 
s = serial.Serial()                        # create a serial port object
s.baudrate = 57600                        # baud rate, in bits/second
s.port = "/dev/ttyAMA0"            # this is whatever port your are using
s.timeout = 3.0
s.open()
 
 
DXL_REG_CCW_Angle_Limit = 8 #to change control mode
DXL_REG_Goal_Postion = 30
DXL_REG_Moving_Speed = 32
 
 
def writeShort(val):
        s.write(chr(int(val)%256))
        s.write(chr(int(val)>>8))
 
def writeWord(ID, addr, val):
        s.write('W'+'w'+chr(ID))
        writeShort(addr)
        writeShort(val)
 
def jointMode(ID):
        s.write('W'+'j'+chr(ID))
 
def setPosition(ID, pos, vel):
        s.write('W'+'p'+chr(ID))
        writeShort(pos)
        writeShort(vel)
 
 
 
 
def moveToDxAngle(ID,dxlPosition,dxlSpeed):
        setPosition(ID,dxlPosition,dxlSpeed)
 
def moveToDegAngle(ID, degPosition, pcSpeed):
        while degPosition > 180:
                degPosition = degPosition - 360
        while degPosition < -180:
                degPosition = degPosition + 360
 
        if (degPosition < -150):
                degPosition = -150
        if (degPosition > 150):
                degPosition = 150
        moveToDxAngle(ID, int(float(degPosition)*3.41+511.5), int(float(pcSpeed)*10.23))
 
def spinAtDxSpeed(ID,dxlSpeed):
        writeWord(ID,DXL_REG_Moving_Speed,dxlSpeed)
 
# Spins at a certain percent of full speed.
def spinAtPcSpeed(ID,pcSpeed):
        if pcSpeed >= 0:
                spinAtDxSpeed(ID,int(float(pcSpeed)*10.23))
        else:
                spinAtDxSpeed(ID,1024+int(float(-pcSpeed)*10.23))
 
def throttleSteeringToLeftRight(inThrottle, inSteering):
        left = min(100, max(-100, inThrottle - inSteering));
        right = min(100, max(-100, inThrottle + inSteering));
        return (left, right)
 
 
 
# Purge the first value
joystate = sixaxis.get_state()
time.sleep(0.5)
print("Press [triangle] to exit.")
shoulderPos = 225
tiltPos = 220
panPos = 0
clawPos = 800
 
# Set wheel and joint modes.
writeWord(1, DXL_REG_CCW_Angle_Limit, 0)
writeWord(2, DXL_REG_CCW_Angle_Limit, 0)
writeWord(3, DXL_REG_CCW_Angle_Limit, 0)
writeWord(4, DXL_REG_CCW_Angle_Limit, 0)
 
 
jointMode(5)
jointMode(6)
jointMode(7)
 
 
while(1):
        joystate = sixaxis.get_state()
        if (joystate['ps'] == True):
                break
    #--------Left Side----------
        if joystate['trig0'] == True:
                spinAtPcSpeed(2, -100)
                spinAtPcSpeed(4, -100)
                print ('Left Back')
        else:
                if joystate['trig2'] == True:
                        spinAtPcSpeed(2, 100)
                        spinAtPcSpeed(4, 100)
                        print ('Left Forward')
                else:
                        spinAtPcSpeed(2, 0)
                        spinAtPcSpeed(4, 0)
        #---------Right Side---------
        if joystate['trig1'] == True:
                spinAtPcSpeed(1, 100)
                spinAtPcSpeed(3, 100)
                print ('Right Back')
        else:
                if joystate['trig3'] == True:
                        spinAtPcSpeed(1, -100)
                        spinAtPcSpeed(3, -100)
                        print ('Right Forward')
                else:
                        spinAtPcSpeed(1, 0)
                        spinAtPcSpeed(3, 0)
               
       
        os.system('cls' if os.name == 'nt' else 'clear')
 
        tiltSpeed = 0
        panSpeed = 0
        shoulderSpeed = 0
        clawSpeed = 0
       
        if joystate['buttonup'] == True:
                shoulderPos = shoulderPos + 10
                shoulderSpeed = 5
        if joystate['buttondown'] == True:
                shoulderPos = shoulderPos - 10
                shoulderSpeed = 5
        if joystate['triangle'] == True:
                tiltPos = tiltPos + 10
                tiltSpeed = 5
        if joystate['cross'] == True:
                tiltPos = tiltPos - 10
                tiltSpeed = 5
        if joystate['buttonleft'] == True:
                clawPos = clawPos - 10
                clawSpeed = 5
        if joystate['buttonright'] == True:
                clawPos = clawPos + 10
                clawSpeed = 5
               
               
        shoulderPos = max(220, min(800, shoulderPos))
        tiltPos = max(220, min(813, tiltPos))
        clawPos = max(400, min(1023, clawPos))
       
               
 
        # Shoulder is limited to -90 and 150. Note that this will hit the ground (which could be desired).
        #shoulderPos = max(-90, min(150, shoulderPos))
 
 
        # Cross resets.
       
 
        tiltcmd = tiltPos + shoulderPos
        pancmd = panPos
 
        # Tilt is limited to 90 degrees, pan to 150.
        tiltcmd = max(-90, min(90, tiltcmd))
        pancmd = max(-150, min(150, pancmd))
       
        moveToDxAngle(5, shoulderPos, shoulderSpeed)
        moveToDxAngle(6, tiltPos, tiltSpeed)
        moveToDxAngle(7, clawPos, clawSpeed)
 
        time.sleep(0.05)
 
sixaxis.shutdown()
print("Exiting.")