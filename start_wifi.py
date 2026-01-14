'''
Boilerplate to setup wifi on pico W
initial time.time() is 1609459200, Fri Jan  1 02:00:00 2021
is_connected_to_wifi():
connect_to_home(credentials):
killswitch():
start_wifi():
'''
import os
import json
import errno
import time
import machine
import network
from startup_helper import access_point, setup_wifi, display_configured_wifi, change_hotspot, connect_to_wifi
import startup_cfg as st_c
wifi_max_attempts = st_c.wifi_max_attempts

def is_connected_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def connect_to_home(credentials):
    # on failure to connect will spend 30s trying
    # with default wifi_max_attempts
    wifi_current_attempt = 0
    while wifi_current_attempt < wifi_max_attempts:
        wifi_current_attempt += 1
        ip_address, state = connect_to_wifi(credentials, 10)
        if is_connected_to_wifi():
            return ip_address, state
    return None, None

def killswitch():
    try:
        os.remove(st_c.ap_start_file)
        started = True
    except OSError:
        started = False

    if started:
        try:
            os.remove(st_c.ap_kill_file)
        except OSError:
            pass
    else:
        try:
            with open(st_c.ap_kill_file, "r") as f:
                v = f.read()
            val = int(v)
            val += 1
            if val > st_c.kill_count:
                f.close()
                os.remove(st_c.ap_kill_file)
                try:
                    os.remove(st_c.wifi_json_file)
                except OSError:
                    pass
                try:
                    os.remove(st_c.ap_status_file)
                except OSError:
                    pass

                time.sleep(2)
                machine.reset()
            with open(st_c.ap_kill_file, "w") as f:
                f.write(str(val))

        except OSError:
            with open(st_c.ap_kill_file, "w") as f:
                f.write('1')
            pass
        # time.sleep(30)

def start_wifi():
    try:
        os.stat(st_c.ap_status_file)
        with open(st_c.ap_status_file) as sf:
            my_status = sf.readline()
            sf.close()

        if my_status == 'STATION':
            with open(st_c.wifi_json_file) as f:
                wifi_credentials = json.load(f)
                if "save" in wifi_credentials:
                    del wifi_credentials['save']
                home_ip, state = connect_to_home(wifi_credentials)
                if not home_ip:
                    killswitch()
                    return None
            return 'STATION'

        elif my_status == 'ACCESS_POINT':
            killswitch()
            try:
                with open(st_c.wifi_json_file) as f:
                    wifi_credentials = json.load(f)
                    if "wifi_pass" in wifi_credentials:
                        password = wifi_credentials["wifi_pass"]
                        ssid = wifi_credentials["ssid"]
            except OSError as e:
                if e.errno == errno.ENOENT:
                    ssid = None
                    password = None
            if ssid:
                ap_name = ssid
            else:
                ap_name = st_c.hotspot_name

            ap = access_point(ap_name, password)
            # error handling for access point?
            home_ip = ap.ifconfig()[0]
            # allow time for killswitch reset (user cycles power before app startup)
            time.sleep(st_c.startup_delay)
            try:
                open(st_c.ap_start_file, "w").close()
            except OSError:
                pass
            return 'ACCESS_POINT'

        elif my_status == 'INTERIM_AP':
            try:
                with open(st_c.wifi_json_file) as f:
                    wifi_credentials = json.load(f)
                    if "ssid" in wifi_credentials:
                        ssid = wifi_credentials["ssid"]
            except OSError as e:
                if e.errno == errno.ENOENT:
                    ssid = st_c.hotspot_name
            change_hotspot(wifi_credentials, ssid)    # reboots...

        elif my_status == 'CONFIGURED':
            display_configured_wifi()   # reboots...

    except OSError as exc:
        if exc.errno == errno.ENOENT:
            try:
                # remove the wifi config file if it exists
                os.remove(st_c.wifi_json_file)
            except OSError as exc1:
                if exc1.errno == errno.ENOENT:
                    pass
        else:
            pass
        # setup wifi
        # scans for ssids
        # starts access point
        # allows choice of access point or ssid
        # if ssid, connects and displays IP
        # sets status to STATION, ACCESS_POINT, INTERIM_AP or CONFIGURED
        setup_wifi()
