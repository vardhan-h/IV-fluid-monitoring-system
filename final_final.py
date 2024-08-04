import machine
import time
import utime
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import uasyncio as asyncio

# Initialize I2C and LCD
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(1, sda=machine.Pin(26), scl=machine.Pin(27), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Initialize IR sensors and variables
ir_pin_drop = machine.Pin(15, machine.Pin.IN)
ir_pin_drip = machine.Pin(14, machine.Pin.IN)
drop_count = 0
bottle_status = 0
start_time = time.ticks_ms()
last_display_time = start_time

# Function to monitor drop count
async def monitor_drops():
    global drop_count, last_display_time
    while True:
        ir_state_drop = ir_pin_drop.value()
        if ir_state_drop == 0:
            drop_count += 1
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_display_time) >= 10000:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("DROP/10 sec: " + str(drop_count))
            drop_count = 0
            last_display_time = current_time
#             if bottle_status < 2:
#                 break
        await asyncio.sleep_ms(1)

# Function to monitor bottle level
async def monitor_bottle():
    global bottle_status
    while True:
        ir_state_drip = ir_pin_drip.value()
        if ir_state_drip == 0:
            bottle_status += 1
            if bottle_status < 2:
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("The bottle is")
                lcd.move_to(0, 1)
                lcd.putstr("about to empty!!")
            break
        await asyncio.sleep_ms(500)

# Create and run event loop
async def main():
    await asyncio.gather(
        monitor_drops(),
        monitor_bottle()
    )

asyncio.run(main())
