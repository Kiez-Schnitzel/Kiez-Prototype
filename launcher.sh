# https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
# https://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/

#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/Kiez-Prototype
sudo python3 kieztalk.py
cd /
