# WiFind-pico
## Howto
Download the code and copy it onto a pico-W.
Download Miguel Grinberg's microdot code from
https://github.com/miguelgrinberg/microdot
Only microdot.py is required. Copy it into the 'external' directory on the pico.

The pico will start a WiFi hotspot (Hotspot) with no password.
Connect to the hotspot and open 192.168.4.1 in a web browser.
A list of available WiFi networks will be displayed. Choose a network and
an IP address. (Most routers allocate low addresses so try an IP between
100 and 200)

Enter the password for the chosen network and save.
The pico will attempt to connect to the selected WiFi network and allocate
the requested address. During this process, the pico hotspot will disappear.
When the pico hotspot (Hotspot) restarts, reconnect to 192.168.4.1

You should see a "connected to" message and the provided IP and MAC addresses.
Press the "reboot" button and the pico should connect to the chosen WiFi
network with the requested address.
Connect to the chosen WiFi network and browse to the provided address.
You should get a "hello world in STATION mode" webpage.

If you choose to keep the Hotspot a password is required. A new page will
be displayed allowing you to change the hotspot name. When complete,
save and the pico will restart.
Connect to the hotspot and browse to 192.168.4.1.
You should get a "hello world in ACCESS_POINT mode" webpage.

To start your own application:
Alter the application.py script to import and start your application.



