# WiFind-pico

## Overview
WiFind was created because I wanted to be able to build a WiFi application on
a pico-W without defining the network information as part of the build. 
It allows a pico-W to run in Station mode (connected to a WiFi network) or
Access point mode (own hotspot).
WiFind initially discovers and connects to WiFi networks and thereafter just
connects to the defined network and starts your application.

## Documentation
WiFind consists of:
### main.py
Sets up directory structure, starts wifi and passes control to application.
The application is assumed to be in a file named application.py containing
a startup function called start_app()  
Application flow is based on the contents of a status (/.secrets/status)
file containing a WiFi status keyword.

### start_wifi.py
Depending on the status value, either starts the application or discovers
available WiFi networks then starts an open access hotspot allowing 
network configuration.

If the status file contains 'STATION', connects to predefined station and
returns 'STATION' or clears status and restarts. See 'no status' below.  
if the saved network is down, the connection attempt will timeout after
30s. To connect, restart the network and power cycle the pico.  
Otherwise if the saved network has been removed or the password changed,
wait 30s for connection timeout amd power cycle the pico.
Repeat 3 times and the pico will clear its saved network configuration 
and restart in hotspot mode.

If the status file contains 'ACCESS_POINT', waits for startup_delay seconds
before returning 'ACCESS_POINT'.
The delay (default 30s) is to cater for a forgotten access point password.
In access point mode, if the user has forgotten the password, the pico can
be reset by power cycling it before the 30s timeout.
Repeat 3 times and the pico will clear its hotspot configuration and
restart in default hotspot mode allowing fresh configuration.
If the power is not cycled within the delay interval, the reset count is
cleared and the application is started.

These steps are available during the network configuration process.
If the status file contains 'CONFIGURED', displays the allocated IP address
and the pico's MAC address and when 'save' is selected updates the status
to 'STATION' and reboots to connect to the desired network.

If the status file contains 'INTERIM_AP', displays a web page allowing
hotspot name change and when 'save' is selected updates the status to
'ACCESS_POINT' and reboots.

If no status file exists, calls setup_wifi from startup_helper.py

### startup_helper.py

setup_wifi scans for WiFi networks and displays their SSIDs in order of
strength.
SSIDs are scanned multiple times within a minute and are only displayed if 
they are detected on each scan and have an acceptable signal strength.
A web page is diaplayed allowing the selection of a WiFi network.
On selection, the status file is updated with 'CONFIGURED' or 'INTERIM_AP'.

### wifi_pages.py

Renders the various web pages.

### startup_cfg.py

Contains configuration parameters.

### external/

Save microdot.py into this directory.  
Contains an old version of uping.py. Used to determine whether a selected IP
address is in use or not. The current version of uping.py from github does
not seem to accept an IP address.
