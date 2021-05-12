 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 # IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 
from machine import Pin, PWM, freq
import time
import select
import sys
import machine

version = "1.0"
version_date = "210510"

# invert relay outputs
rel_inv = 0 # set = 1 to invert outputs
# enable pwm outputs, set to 1
pwm_on  = 1
# meade lx10 handcontroller inputs
sup_pin   = Pin(5, Pin.OUT)
sup_pin.value(1)
n_lx10hc  = Pin(6, Pin.IN, Pin.PULL_UP)
s_lx10hc  = Pin(7, Pin.IN, Pin.PULL_UP)
e_lx10hc  = Pin(8, Pin.IN, Pin.PULL_UP)
w_lx10hc  = Pin(9, Pin.IN, Pin.PULL_DOWN)
# st-4 inputs
e_st4     = Pin(10, Pin.IN, Pin.PULL_UP)
n_st4     = Pin(11, Pin.IN, Pin.PULL_UP)
s_st4     = Pin(12, Pin.IN, Pin.PULL_UP)
w_st4     = Pin(13, Pin.IN, Pin.PULL_UP)

# outputs
if pwm_on == 1:
    n_pwm  = PWM(Pin(14))
    s_pwm  = PWM(Pin(15))
    ew_pwm = PWM(Pin(16))
    in_pin = Pin(17, Pin.IN, Pin.PULL_UP)
out_North  = Pin(18, Pin.OUT)
out_South  = Pin(19, Pin.OUT)
out_East   = Pin(20, Pin.OUT)
out_West   = Pin(21, Pin.OUT)
led25      = Pin(25, Pin.OUT)

# pwm setup
if pwm_on == 0:
    ew_pwm.freq(400)
    ew_normal = 32000
    ew_fast   = 65535
    ew_pwm.duty_u16(ew_normal)
    n_pwm.freq(200)
    n_normal  = 0
    n_pwm.duty_u16(n_normal)
    s_pwm.freq(200)
    s_normal  = 0
    ns_fast   = 65535
    s_pwm.duty_u16(s_normal)
    last_state = 1

    # setup variables
    freq_set    = 20.89
    freq_limit  = 0.005
    motor_ctrl  = 1
    report_ctrl = 0
    motor_corr  = 1250
    speed_count_set = 10
    rep_count_set   = 10

# initialise parameters
lenEast  = 0
lenWest  = 0
lenSouth = 0
lenNorth = 0
End_North = time.ticks_us()
out_North.value(rel_inv)
End_East = time.ticks_us()
out_East.value(rel_inv)
End_South = time.ticks_us()
out_South.value(rel_inv)
End_West = time.ticks_us()
out_West.value(rel_inv)
timeout = time.ticks_us() + 3000000
speed_total = 0
speed_count = 0
rep_count   = 0
rep_total   = 0
rel_nor     = 1
if rel_inv == 1:
    rel_nor = 0

while True:
    # respond to LX10 Handcontroller or ST-4 inputs
    if (n_lx10hc.value() == 0 or n_st4.value() == 0) and lenSouth == 0:
        out_South.value(rel_inv)
        out_North.value(rel_nor)
        if pwm_on == 1:
            n_pwm.duty_u16(ns_fast)
            s_pwm.duty_u16(0)
        lenNorth = 2
    elif n_lx10hc.value() == 1 and n_st4.value() == 1 and lenNorth == 2:
        out_North.value(rel_inv)
        if pwm_on == 1:
            n_pwm.duty_u16(0)
        lenNorth = 0
    if (s_lx10hc.value() == 0  or s_st4.value() == 0) and lenNorth == 0:
        out_South.value(rel_nor)
        out_North.value(rel_inv)
        if pwm_on == 1:
            n_pwm.duty_u16(0)
            s_pwm.duty_u16(ns_fast)
        lenSouth = 2
    elif s_lx10hc.value() == 1 and  s_st4.value() == 1 and lenSouth == 2:
        out_South.value(rel_inv)
        if pwm_on == 1:
            s_pwm.duty_u16(0)
        lenSouth = 0
    if (e_lx10hc.value() == 0  or e_st4.value() == 0) and lenWest == 0:
        out_West.value(rel_inv)
        out_East.value(rel_nor)
        if pwm_on == 1:
            ew_pwm.duty_u16(0)
        lenEast = 2
    elif e_lx10hc.value() == 1 and e_st4.value() == 1 and lenEast == 2:
        out_East.value(rel_inv)
        if pwm_on == 1:
            ew_pwm.duty_u16(ew_normal)
        lenEast = 0
    if (w_lx10hc.value() == 1  or w_st4.value() == 0) and lenEast == 0:
        out_West.value(rel_nor)
        out_East.value(rel_inv)
        if pwm_on == 1:
            ew_pwm.duty_u16(ew_fast)
        lenWest = 2
    elif w_lx10hc.value() == 0 and w_st4.value() == 1 and lenWest == 2:
        out_West.value(rel_inv)
        if pwm_on == 1:
            ew_pwm.duty_u16(ew_normal)
        lenWest = 0
        
    # check serial input for commands   
    if select.select([sys.stdin],[],[],0)[0]:
       ch = sys.stdin.read(1)
       if ch[0] == ":":
          ch = sys.stdin.read(1)
          if ch[0] == "G":
              ch = sys.stdin.read(1)
              if ch[0] == "R":
                  print("00:00.0#")
              elif ch[0] == "S":
                  print("00:00:00#")
              elif ch[0] == "W":
                  print("AT0")
              elif ch[0] == "Z":
                  print("000*00'00#")
              elif ch[0] == "D":
                  print("s00*00'00#")
              elif ch[0] == "A":
                  print("s00*00'00#")
              elif ch[0] == "t":
                  print("s00*00#")
              elif ch[0] == "V":
                  ch = sys.stdin.read(1)
                  if ch[0] == "T":
                      print("00:00:00#")
                  elif ch[0] == "P":
                      print("ETX Autostar#")
                  elif ch[0] == "F":
                      print("ETX Autostar#")
                  elif ch[0] == "N":
                      print(version)
                  elif ch[0] == "D":
                      print(version_date)
          elif ch[0] == "?":
              ch = sys.stdin.read(1)
              if ch[0] == "+":
                  print("00:00:00#")
          # set motor volts (eg. :RAV37000)        
          elif ch[0] == "R":
              ch = sys.stdin.read(1)
              if ch[0] == "A":
                  ch = sys.stdin.read(1)
                  if ch[0] == "V":
                      ch1 = sys.stdin.read(1)
                      ch2 = sys.stdin.read(1)
                      ch3 = sys.stdin.read(1)
                      ch4 = sys.stdin.read(1)
                      ch5 = sys.stdin.read(1)
                      out = ch1+ch2+ch3+ch4+ch5
                      if ord(ch5) > 47 and ord(ch5) < 58:
                          ew_normal = int(out)
                          ew_pwm.duty_u16(ew_normal)
        
          elif ch[0] == "M":
              ch = sys.stdin.read(1)
              speed_count = 0
              speed_total = 0
              # set motor control ON/OFF (:MCO)
              if ch[0] == "C" and pwm_on == 1:
                  ch = sys.stdin.read(1)
                  if ch[0] == "O":
                      motor_ctrl = 1
                  elif ch[0] == "o":
                      motor_ctrl = 0
              # set report_ctrling (via serial) ON/OFF (:MRO)
              elif ch[0] == "R" and pwm_on == 1:
                  ch = sys.stdin.read(1)
                  if ch[0] == "O":
                      report_ctrl = 1
                  elif ch[0] == "o":
                      report_ctrl = 0
              # move commands (eg. :Mn)
              elif ch[0] == "n":
                  out_South.value(rel_inv)
                  out_North.value(rel_nor)
                  led25.value(1)
                  if pwm_on == 1:
                      n_pwm.duty_u16(ns_fast)
                      s_pwm.duty_u16(0)
                  lenNorth = 3
              elif ch[0] == "s":
                  out_North.value(rel_inv)
                  out_South.value(rel_nor)
                  led25.value(1)
                  if pwm_on == 1:
                      s_pwm.duty_u16(ns_fast)
                      n_pwm.duty_u16(0)
                  lenSouth = 3
              elif ch[0] == "e":
                  out_West.value(rel_inv)
                  out_East.value(rel_nor)
                  led25.value(1)
                  if pwm_on == 1:
                      ew_pwm.duty_u16(0)
                  lenEast = 3
              elif ch[0] == "w":
                  out_East.value(rel_inv)
                  out_West.value(rel_nor)
                  led25.value(1)
                  if pwm_on == 1:
                      ew_pwm.duty_u16(ew_fast)
                  lenWest = 3
            
            # move for a period commands (eg :Mgn1000)       
              elif ch[0] == "g":
                  chd = sys.stdin.read(1)
                  ch1 = sys.stdin.read(1)
                  ch2 = sys.stdin.read(1)
                  ch3 = sys.stdin.read(1)
                  ch4 = sys.stdin.read(1)
                  out = ch1+ch2+ch3+ch4
                  
                  if chd == "n" and ord(ch4) > 47 and ord(ch4) < 58:
                      lenNorth = 1
                      lenSouth = 0
                      out_South.value(rel_inv)
                      out_North.value(rel_nor)
                      led25.value(1)
                      if pwm_on == 1:
                          s_pwm.duty_u16(0)
                          n_pwm.duty_u16(ns_fast)
                      End_North = time.ticks_us() + (int(out) * 1000)
                  elif chd == "e" and ord(ch4) > 47 and ord(ch4) < 58:
                      lenEast = 1
                      lenWest = 0
                      out_West.value(rel_inv)
                      out_East.value(rel_nor)
                      led25.value(1)
                      End_East = time.ticks_us() + (int(out) * 1000)
                      if pwm_on == 1:
                          ew_pwm.duty_u16(0)
                      timeout = End_East + 3000000
                  elif chd == "s" and ord(ch4) > 47 and ord(ch4) < 58:
                      lenSouth = 1
                      lenNorth = 0
                      out_North.value(rel_inv)
                      out_South.value(rel_nor)
                      led25.value(1)
                      if pwm_on == 1:
                          n_pwm.duty_u16(0)
                          s_pwm.duty_u16(ns_fast)
                      End_South = time.ticks_us() + (int(out) * 1000)
                  elif chd == "w" and ord(ch4) > 47 and ord(ch4) < 58:
                      lenWest = 1
                      lenEast = 0
                      out_East.value(rel_inv)
                      out_West.value(rel_nor)
                      led25.value(1)
                      End_West = time.ticks_us() + (int(out) * 1000)
                      if pwm_on == 1:
                          ew_pwm.duty_u16(ew_fast)
                      timeout = End_West + 3000000

          # quit move commands  (eg. :Qn)   
          elif ch[0] == "Q":
              ch = sys.stdin.read(1)
              if ch[0] == "#" or ch[0] == "n":
                  lenNorth = 0
                  lenSouth = 0
                  out_North.value(rel_inv)
                  led25.value(0)
                  if pwm_on == 1:
                      n_pwm.duty_u16(0)
              if ch[0] == "#" or ch[0] == "s":
                  lenSouth = 0
                  lenNorth = 0
                  out_South.value(rel_inv)
                  led25.value(0)
                  if pwm_on == 1:
                      s_pwm.duty_u16(0)
              if ch[0] == "#" or ch[0] == "w":
                  lenWest = 0
                  out_West.value(rel_inv)
                  led25.value(0)
                  timeout = time.ticks_us() + 3000000
                  if pwm_on == 1:
                      ew_pwm.duty_u16(ew_normal)
              if ch[0] == "#" or ch[0] == "e":
                  lenEast = 0
                  out_East.value(rel_inv)
                  led25.value(0)
                  timeout = time.ticks_us() + 3000000
                  if pwm_on == 1:
                      ew_pwm.duty_u16(ew_normal)

    # check motor speed        
    if lenEast == 0 and lenWest == 0 and (time.ticks_us() > timeout or timeout - time.ticks_us() > 10000000) and pwm_on == 1:
        # get in sync with motor
        time_out = time.ticks_us()
        countp = 0
        while countp < 2 and time.ticks_diff(time.ticks_us(), time_out) < 40000 :
            x = in_pin.value()
            if x != last_state:
                countp += 1
                last_state = x
        # measure motor frequency
        countp = 0
        speed_count += 1
        start2 = time.ticks_us()
        while countp < 6 and time.ticks_diff(time.ticks_us(), start2) < 200000:
            x = in_pin.value()
            if x != last_state:
              countp += 1
              last_state = x
        end = time.ticks_diff(time.ticks_us(), start2)
        freq = 1000000 / end
        speed_total += freq
        # after measurements take average
        if speed_count > speed_count_set:
            freq = speed_total / speed_count
            if (freq > freq_set - 10 and freq < freq_set + 10) and motor_ctrl == 1:
                  # vary motor speed if required
                  if freq < freq_set - freq_limit or freq > freq_set + freq_limit:
                    ew_normal += int((freq_set - freq) * motor_corr)
                    if ew_normal > 60000 or ew_normal < 20000:
                        ew_normal -= int((freq_set - freq) * motor_corr)
                    ew_pwm.duty_u16(ew_normal)
                    timeout = time.ticks_us()
            speed_count = 0
            speed_total = 0
            rep_count += 1
            rep_total += freq
            if rep_count > rep_count_set:
                freq = rep_total / rep_count
                if report_ctrl == 1:
                    print(str(ew_normal),":",str(freq))
                rep_count = 0
                rep_total = 0
                                
    # end timed move outputs
    if (time.ticks_us() > End_North or End_North - time.ticks_us() > 10000000) and lenSouth == 0 and lenNorth == 1:
        lenNorth = 0
        out_North.value(rel_inv)
        led25.value(0)
        if pwm_on == 1:
            n_pwm.duty_u16(0)
    if (time.ticks_us() > End_East or End_East - time.ticks_us() > 10000000) and lenWest == 0 and lenEast == 1:
        lenEast = 0
        out_East.value(rel_inv)
        led25.value(0)
        if pwm_on == 1:
            ew_pwm.duty_u16(ew_normal)
    if (time.ticks_us() > End_South or End_South - time.ticks_us() > 10000000) and lenSouth == 1 and lenNorth == 0:
        lenSouth = 0
        out_South.value(rel_inv)
        led25.value(0)
        if pwm_on == 1:
            s_pwm.duty_u16(0)
    if (time.ticks_us() > End_West or End_West - time.ticks_us() > 10000000) and lenEast == 0 and lenWest == 1:
        lenWest = 0
        out_West.value(rel_inv)
        led25.value(0)
        if pwm_on == 1:
            ew_pwm.duty_u16(ew_normal)
        
        
        