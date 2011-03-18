avrdude -p atmega32u4 -P usb -B 1 -c usbtiny -U flash:w:BootloaderDFU.hex -U lfuse:w:0xFC:m -U hfuse:w:0xD0:m
avrdude -p atmega32u4 -P usb -B 1 -c usbtiny -D -U flash:w:USBtoSerial.hex
avrdude -p atmega32u4 -P usb -c usbtiny -D -U lfuse:w:0xde:m -U hfuse:w:0xd9:m -U lock:w:0x29:m -v
pause
