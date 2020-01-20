import sys
sys.path.append("./lib")

import i2c_lib
from time import *

# LCD Address
ADDRESS = 0x27

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Offset for up to 4 rows.
LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class lcd:
   #initializes objects and lcd
   def __init__(self):
      self.lcd_device = i2c_lib.i2c_device(ADDRESS)

      # Save column and line state.
      self._cols = 16
      self._lines = 2

      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)

      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)

      # # Initialize the display.
      # self.write8(0x33)
      # self.write8(0x32)
      # # Initialize display control, function, and mode registers.
      self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
      # self.displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_2LINE | LCD_5x8DOTS
      self.displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
      # # Write registers.
      # self.write8(LCD_DISPLAYCONTROL | self.displaycontrol)
      # self.write8(LCD_FUNCTIONSET | self.displayfunction)
      # self.write8(LCD_ENTRYMODESET | self.displaymode)  # set the entry mode
      # self.clear()

      sleep(0.2)

   # clocks EN to latch command
   def lcd_strobe(self, data):
      self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
      sleep(.0005)
      self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
      sleep(.0001)

   def lcd_write_four_bits(self, data):
      self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
      self.lcd_strobe(data)

   # write a command to lcd
   def lcd_write(self, cmd, mode=0):
      self.lcd_write_four_bits(mode | (cmd & 0xF0))
      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))
      
   #turn on/off the lcd backlight
   def lcd_backlight(self, state):
      if state in ("on","On","ON"):
         self.lcd_device.write_cmd(LCD_BACKLIGHT)
      elif state in ("off","Off","OFF"):
         self.lcd_device.write_cmd(LCD_NOBACKLIGHT)
      else:
         print("Unknown State!")

   # put string function
   def lcd_messageToLine(self, string, line):
      if line == 1:
         self.lcd_write(0x80)
      if line == 2:
         self.lcd_write(0xC0)
      if line == 3:
         self.lcd_write(0x94)
      if line == 4:
         self.lcd_write(0xD4)

      for char in string:
         self.lcd_write(ord(char), Rs)
   
   def lcd_set_cursor(self, col, row):
      """Move the cursor to an explicit column and row position."""
      # Clamp row to the last row of the display.
      if row > self._lines:
         row = self._lines - 1
      # Set location.
      self.lcd_write(LCD_SETDDRAMADDR | (col + LCD_ROW_OFFSETS[row]))

   def lcd_show_cursor(self, show):
      """Show or hide the cursor.  Cursor is shown if show is True."""
      if show:
         self.displaycontrol |= LCD_CURSORON
      else:
         self.displaycontrol &= ~LCD_CURSORON
      self.lcd_write(LCD_DISPLAYCONTROL | self.displaycontrol)

   def lcd_move_left(self):
      """Move display left one position."""
      # if line == 1:
      #    # self.lcd_write(0x80)
      #    self.lcd_write(0x80 | LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)
      # if line == 2:
      #    # self.lcd_write(0xC0)
      #    print("gg")
      self.lcd_write(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)
      

   def autoscroll(self, autoscroll):
      """Autoscroll will 'right justify' text from the cursor if set True,
      otherwise it will 'left justify' the text.
      """
      if autoscroll:
         self.displaymode |= LCD_ENTRYSHIFTINCREMENT
      else:
         self.displaymode &= ~LCD_ENTRYSHIFTINCREMENT
      self.lcd_write(LCD_ENTRYMODESET | self.displaymode)
   
   # clear lcd and set to home
   def lcd_clear(self):
      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_RETURNHOME)

   # Enable or disable the display.  Set enable to True to enable
   def enable_display(self, enable):
      if enable:
         self.displaycontrol |= LCD_DISPLAYON
      else:
         self.displaycontrol &= ~LCD_DISPLAYON
      self.lcd_write(LCD_DISPLAYCONTROL | self.displaycontrol)
