'''
functions called to setup wifi
Some functions may be required by the application
scan_ssids():
access_point(ssid, password = None):
connect_to_wifi(credentials, timeout_seconds=30):
checksum(data):
ping(host, count=4, timeout=5000, interval=10, quiet=False, size=64):
setup_wifi():
my_mac():
display_configured_wifi():
change_hotspot(wifi_json, ssid):
'''
# pylint: disable=expression-not-assigned, missing-function-docstring, unspecified-encoding, line-too-long
import time
import machine
import os
import network
import json
import utime
import uselect
import uctypes
import usocket
import ustruct
import urandom
import binascii
import re
from microdot.microdot import Microdot, send_file
from wifi_pages import render_configure_wifi, render_configured_wifi, render_change_hotspot
import startup_cfg as st_c

wifi_max_attempts = st_c.wifi_max_attempts

def scan_ssids():
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    except OSError as exc:
        aps = None

    repeats = st_c.scan_count
    scans = {}
    channels = {}
    strength = {}
    for i in range(repeats):
        try:
            aps = wlan.scan()
        except OSError as exc:
            aps = None

        # 2.4GHz channels 1, 6 and 11 don't overlap
        for ap in aps:
            ssid = ap[0].decode()
            if not ssid:
                ssid = 'unknown/hidden'
            channel = int(ap[2])
            rssi = ap[3]
            if ssid not in strength:
                scans[ssid] = 0
                strength[ssid] = []
            strength[ssid].append(rssi)
            scans[ssid] += 1
            if channel not in channels:
                channels[channel] = []
            if not ssid in channels[channel]:
                channels[channel].append(ssid)    # add ssid to channels list

        if i < repeats-1:
            time.sleep(10)
    wlan.active(False)

    wifi_json = {"access_points": []}
    wifi_json["warn"] = []
    # weak networks - below st_c.signal_limit (-70) are ignored
    poor = ''
    access_sort = {}
    for ssid, stren in strength.items():
        sig_stren = sum(strength[ssid]) / len(strength[ssid])
        if not sig_stren in access_sort:
            access_sort[sig_stren] = []
        access_sort[sig_stren].append(ssid)
        if scans[ssid] < repeats:
            wifi_json["warn"].append(f"{ssid} is unstable {scans[ssid]}/{repeats}")
        elif sig_stren < st_c.signal_limit:
            wifi_json["warn"].append(f"{ssid} is weak")
        elif sig_stren < st_c.signal_poor:
            wifi_json["warn"].append(f"{ssid} is poor")
            poor = '"poor" WiFi points may be unreliable'

    for sig_stren, ssids in sorted(access_sort.items(), reverse = True):
        # only include stronger signals
        if sig_stren > st_c.signal_limit:
            for ssid in ssids:
                wifi_json["access_points"].append(ssid)

    # 2.4GHz channels 1, 6 and 11 don't overlap
    good_channels = [ 1, 6, 11 ]
    suggest_channels = False
    for chan, ssids in channels.items():
        if len(ssids) > 1:
            ssid_str = ''
            i = 1
            for ssid in ssids:
                sep = ','
                if i == len(ssids) -1:
                    sep = ' and'
                elif i == len(ssids):
                    sep = ''
                ssid_str += str(ssid) + sep + ' '
                i += 1
            wifi_json["warn"].append(f"{ssid_str} use channel {chan}")
            suggest_channels = True
            if chan in good_channels:
                good_channels.remove(chan)

    if suggest_channels and good_channels:
        ch_str = ''
        i = 0
        for ch in good_channels:
            i += 1
            sep = ','
            if i == len(good_channels) -1:
                sep = ' or'
            elif i == len(good_channels):
                sep = ''
            ch_str += str(ch) + sep + ' '

        if len(good_channels) == 1:
            wifi_json["warn"].append(f"Consider using channel {ch_str}")
        else:
            wifi_json["warn"].append(f"Consider using channels {ch_str}")
    if poor:
        wifi_json["warn"].append('"poor" WiFi points may be unreliable')
    return wifi_json

def access_point(ssid, password = None):
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid)
    if password:
        wlan.config(password=password)
    else:
        wlan.config(security=0) # disable password
    wlan.active(True)

    return wlan

def connect_to_wifi(credentials, timeout_seconds=30):
    password = credentials["wifi_pass"]
    ssid = credentials["ssid"]
    preferred_ip = credentials["preferred_ip"]  # This is the short ip because this is the initial startup

    statuses = {
        2: "wtf",
        network.STAT_IDLE: "idle",
        network.STAT_CONNECTING: "connecting",
        network.STAT_WRONG_PASSWORD: "wrong password",
        network.STAT_NO_AP_FOUND: "access point not found",
        network.STAT_CONNECT_FAIL: "connection failed",
        network.STAT_GOT_IP: "got ip address"
    }

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    status = wlan.status()

    while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
        new_status = wlan.status()
        if status != new_status:
            if status in statuses:
                status = new_status
        time.sleep(0.25)

    if not wlan.status() == network.STAT_GOT_IP:
        wlan.active(False)
        return None, statuses[status]

    # if we got our desired IP, it means we rebooted within the DHCP lease interval so we should just carry on...
    if preferred_ip:
        if preferred_ip == wlan.ifconfig()[0]:
            rc = wlan.ifconfig()[0]
            wlan.active(False)
            return rc, "Desired"
    else:
        rc =  wlan.ifconfig()[0]
        wlan.active(False)
        return rc, "DHCP"

    l_ifconfig = list(wlan.ifconfig())

    # construct and ping our preferred IP
    base_ip = '.'.join(wlan.ifconfig()[0].split('.')[0:3]) # 1st 3 octets of IP
    start_ip = int(preferred_ip.split('.')[-1])
    for i in range (start_ip, start_ip + 4):
        desired_ip = base_ip + '.' + str(i)
        sent, rec = ping(desired_ip, 3, 5000, 10, False, 64)
        if rec == 0:
            l_ifconfig[0] = desired_ip
            wlan.ifconfig(tuple(l_ifconfig))
            if wlan.ifconfig()[0] == desired_ip:
                wlan.active(False)
                return desired_ip, None

    rc = None
    wlan.active(False)
    return rc, "In_use"

# µPing (MicroPing) for MicroPython
# copyright (c) 2018 Shawwwn <shawwwn1@gmail.com>
# License: MIT

# Internet Checksum Algorithm
# Author: Olav Morken
# https://github.com/olavmrk/python-ping/blob/master/ping.py
# @data: bytes
def checksum(data):
    if len(data) & 0x1: # Odd number of bytes
        data += b'\0'
    cs = 0
    for pos in range(0, len(data), 2):
        b1 = data[pos]
        b2 = data[pos + 1]
        cs += (b1 << 8) + b2
    while cs >= 0x10000:
        cs = (cs & 0xffff) + (cs >> 16)
    cs = ~cs & 0xffff
    return cs

def ping(host, count=4, timeout=5000, interval=10, quiet=False, size=64):

    # prepare packet
    assert size >= 16, "pkt size too small"
    pkt = b'Q'*size
    pkt_desc = {
        "type": uctypes.UINT8 | 0,
        "code": uctypes.UINT8 | 1,
        "checksum": uctypes.UINT16 | 2,
        "id": uctypes.UINT16 | 4,
        "seq": uctypes.INT16 | 6,
        "timestamp": uctypes.UINT64 | 8,
    } # packet header descriptor
    h = uctypes.struct(uctypes.addressof(pkt), pkt_desc, uctypes.BIG_ENDIAN)
    h.type = 8 # ICMP_ECHO_REQUEST
    h.code = 0
    h.checksum = 0
    h.id = urandom.getrandbits(16)
    h.seq = 1

    # init socket
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
    sock.setblocking(0)
    sock.settimeout(timeout/1000)
    addr = usocket.getaddrinfo(host, 1)[0][-1][0] # ip address
    sock.connect((addr, 1))

    seqs = list(range(1, count+1)) # [1,2,...,count]
    c = 1
    t = 0
    n_trans = 0
    n_recv = 0
    finish = False
    while t < timeout:
        if t==interval and c<=count:
            # send packet
            h.checksum = 0
            h.seq = c
            h.timestamp = utime.ticks_us()
            h.checksum = checksum(pkt)
            if sock.send(pkt) == size:
                n_trans += 1
                t = 0 # reset timeout
            else:
                seqs.remove(c)
            c += 1

        # recv packet
        while 1:
            socks, _, _ = uselect.select([sock], [], [], 0)
            if socks:
                resp = socks[0].recv(4096)
                resp_mv = memoryview(resp)
                h2 = uctypes.struct(uctypes.addressof(resp_mv[20:]), pkt_desc, uctypes.BIG_ENDIAN)
                seq = h2.seq
                if h2.type==0 and h2.id==h.id and (seq in seqs): # 0: ICMP_ECHO_REPLY
                    t_elapsed = (utime.ticks_us()-h2.timestamp) / 1000
                    ttl = ustruct.unpack('!B', resp_mv[8:9])[0] # time-to-live
                    n_recv += 1
                    seqs.remove(seq)
                    if len(seqs) == 0:
                        finish = True
                        break
            else:
                break

        if finish:
            break

        utime.sleep_ms(1)
        t += 1

    # close
    sock.close()
    return (n_trans, n_recv)

def setup_wifi():
    ap_cfg = Microdot()
    wifi_json = scan_ssids()
    wifi_json['access_points'].append(st_c.hotspot_name)
    wifi_json['preferred_ip'] = ''
    wifi_json['wifi_pass'] = ''
    # also can set security level
    # wlan.config(security=4)
    # levels are
    # 0 – open
    # 1 – WEP
    # 2 – WPA-PSK
    # 3 – WPA2-PSK
    # 4 – WPA/WPA2-PSK

    @ap_cfg.route("/", methods=["GET", "POST"])
    def ap_configure(request):
        errors = []
        if request.form:
            creds = request.form
            if 'quit' in creds:
                try:
                    os.remove(st_c.error_file)
                except OSError:
                    pass
                return send_file(f"{st_c.configure_wifi_html_file}")

            # read persistent errors. They were getting lost on page reload.
            try:
                os.stat(st_c.error_file)
                with open(st_c.error_file) as f:
                    errors.append(f.readline())
                os.remove(st_c.error_file)
            except OSError:
                pass
            wifi_json["ssid"] = creds['ssid'].strip()
            wifi_json["wifi_pass"] = creds['wifi_pass'].strip()
            wifi_json["preferred_ip"] = creds['preferred_ip'].strip()
            # in order to get here, save must be set
            if len(wifi_json["wifi_pass"]) == 0 :
                errors.append('please enter a password')
            elif len(wifi_json["wifi_pass"]) < 8:
                errors.append('password too short, try again')
                wifi_json["wifi_pass"] = ''

            # because it's a list box, ssid must be in creds
            if wifi_json["ssid"] == st_c.hotspot_name:
                if wifi_json["preferred_ip"]:
                    errors.append("Hotspot can't have preferred ip")
                    wifi_json["preferred_ip"] = ''
                elif not errors:
                    if "warn" in wifi_json:
                        del wifi_json["warn"]
                    if "access_points" in wifi_json:
                        del wifi_json["access_points"]
                    with open(st_c.wifi_json_file, "w") as f:
                        json.dump(wifi_json, f)
                    with open(st_c.ap_status_file, "w") as f:
                        f.write("INTERIM_AP")
                        f.close()
                    time.sleep(2)
                    machine.reset()

            elif wifi_json["preferred_ip"]:
                p_ip = wifi_json["preferred_ip"] # just to keep things short
                if int(p_ip) < st_c.wifi_static_ip['low'] or \
                        int(p_ip) > st_c.wifi_static_ip['high']:
                    errors.append(f"preferred_ip must be between {st_c.wifi_static_ip['low']} and {st_c.wifi_static_ip['high']}")
                    wifi_json["preferred_ip"] = ''

            if not errors:
                credentials = wifi_json.copy()
                del credentials["access_points"]
                del credentials["warn"]

                home_ip, state = connect_to_wifi(credentials)
                if home_ip:
                    # home_ip is a full ip and not just the host portion
                    # we might not have got the preferred_ip because it was in use
                    # but we would get a higher ip.
                    # unless there were many occupied consecutive addresses
                    credentials['preferred_ip'] = home_ip
                    with open(st_c.wifi_json_file, "w") as f:
                        json.dump(credentials, f)
                        f.close()

                    with open(st_c.ap_status_file, "w") as f:
                        f.write("CONFIGURED")
                        f.close()
                    time.sleep(2)
                    machine.reset()
                else:
                    with open(st_c.error_file, "w") as f:
                        el = f"Can't connect to {wifi_json["ssid"]}"
                        if wifi_json["preferred_ip"]:
                            el += f' using address {wifi_json["preferred_ip"]}'
                        el += '\n'
                        f.write(el)
                        if state:
                            if state == 'connecting':
                                f.write("Wrong password?\n")
                            elif state == 'In_use':
                                f.write("Address in use\n")
                    with open(st_c.ap_status_file, "w") as f:
                        f.write("CONFIGURED")
                        f.close()
                    time.sleep(2)
                    machine.reset()

        render_configure_wifi(wifi_json, errors)
        return send_file(f"{st_c.configure_wifi_html_file}")

    ap = access_point(st_c.hotspot_name)
    # ip = ap.ifconfig()[0]
    ap_cfg.run(port=80)

def my_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan_mac = wlan.config('mac')
    hex_mac = binascii.hexlify(wlan_mac, ':').decode().upper()
    return hex_mac

def display_configured_wifi():
    ap_cfg = Microdot()

    @ap_cfg.route("/", methods=["GET", "POST"])
    def ap_index(request):
        errors = []
        mac = my_mac()
        try:
            with open(st_c.wifi_json_file) as f:
                creds = json.load(f)
                ssid = creds['ssid']
                ip = creds['preferred_ip']
        except OSError as exc:
            ssid = 'unknown'
            ip = 'unknown'
            mac = 'unknown'

        try:
            with open(st_c.error_file) as f:
                errors = f.readlines()
        except OSError:
            pass

        if request.form:
            if 'reboot' in request.form:
                cleanup = True
                try:
                    os.stat(st_c.error_file)
                except OSError:
                    cleanup = False
                if cleanup:
                    try:
                        os.remove(st_c.error_file)
                    except OSError:
                        pass
                    try:
                        os.remove(st_c.ap_status_file)
                    except OSError:
                        pass
                else:
                    with open(st_c.ap_status_file, "w") as f:
                        f.write("STATION")
                        f.close()
                time.sleep(2)
                machine.reset()

        render_configured_wifi(ssid, ip, mac, errors)
        return send_file(f"{st_c.configured_wifi_html_file}")

    ap = access_point(st_c.hotspot_name)
    # ip = ap.ifconfig()[0]
    ap_cfg.run(port=80)

def change_hotspot(wifi_json, ssid):
    ap_cfg = Microdot()
    @ap_cfg.route("/", methods=["GET", "POST"])
    def ap_index(request):
        errors = []
        if request.form:
            # form only has 'save' button
            interim_ssid = request.form['hot_name'].strip()
            if interim_ssid == wifi_json["ssid"]:
                pass
            elif interim_ssid:
                # parse it and either raise errors or write it to wifi.json
                clean_ssid = re.sub(r'[^a-zA-Z0-9_-]', '', interim_ssid)
                if interim_ssid == clean_ssid:
                    wifi_json["ssid"] = interim_ssid
                    with open(st_c.wifi_json_file, "w") as f:
                        json.dump(wifi_json, f)
                        f.close()
                else:
                    errors.append("Invalid characters in name, use letters, numbers, dash or underscore")
            if not errors:
                with open(st_c.ap_status_file, "w") as f:
                    f.write("ACCESS_POINT")
                    f.close()
                time.sleep(2)
                machine.reset()

        render_change_hotspot(ssid, errors)
        return send_file(f"{st_c.change_hotspot_file}")

    try:
        with open(st_c.wifi_json_file) as f:
            creds = json.load(f)
            ssid = creds['ssid']
    except OSError as exc:
        ssid = st_c.hotspot_name
    ap = access_point(ssid)
    ip = ap.ifconfig()[0]
    ap_cfg.run(port=80)
