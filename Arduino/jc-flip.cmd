batchisp -hardware usb -device atmega32u4 -operation erase f
batchisp -hardware usb -device atmega32u4 -operation loadbuffer %6\%8.hex program
rem batchisp -hardware usb -device atmega32u4 -operation memory EEPROM erase
rem batchisp -hardware usb -device atmega32u4 -operation memory EEPROM loadbuffer %6\%8.eep program
batchisp -hardware usb -device atmega32u4 -operation start reset 0