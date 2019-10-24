#
#
# Stand Alone Modbus Program
#
#
#
#
import time
from  myModbus import *

instrument = Instrument("/dev/ttyUSB1",31 )  # 10 is instrument address
instrument.serial.timeout = .1
instrument.serial.parity = serial.PARITY_NONE
#instrument.serial.baudrate = 115200
instrument.serial.baudrate = 38400
instrument.debug = True

print "instrument",instrument.serial
#instrument.address = 10
#debug = None
#write_register(registeraddress, value, numberOfDecimals=0, functioncode=16, signed=False
#read_register(registeraddress, numberOfDecimals=0, functioncode=3, signed=False)[source]
#read_registers(registeraddress, numberOfRegisters, functioncode=3)[source]
#write_registers(registeraddress, values)

#for i in range(0,1):
#  instrument.write_register(0,0,0)
#  print  "register 0", instrument.read_register(0,0)
#  instrument.write_register(0,255,0)
#  print  i,"register 0", instrument.read_register(0,0)

#print "read registers", instrument.read_registers(0,10)
#print "write registers",instrument.write_registers(0,[1,2,3,4,5,6,7,8,9,10])
#print "read registers", instrument.read_registers(0,10)
'''
#print instrument.read_eeprom_registers(0,10)

#print "write registers",instrument.write_eeprom_registers(0,
    [[0,0,0,21],[0,0,0,22],[0,0,0,23],[0,0,0,24],[0,0,0,25],
    [0,0,0,26],[0,0,0,27],[0,0,0,28],[0,0,0,2(module,generator9],[0,0,0,30]])

print "read registers", instrument.read_eeprom_registers(0,10)
'''
#print "read registers", instrument.read_eeprom_registers(0,10)
#instrument.special_command(0,  [0,34] )
for i in range(0,0):
    try:
         print "i",i
         print "read registers",instrument.read_registers(0,20)
    except:
        print "error"
        
#print "write registers",instrument.write_registers(6,[500])
print "read registers", instrument.read_registers(0,1)  

