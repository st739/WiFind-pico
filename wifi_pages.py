'''
render pages for startup wifi
application might call render_change_hotspot, or not
these pages should be reusable
'''
import startup_cfg as st_c

def render_change_hotspot(ssid, errors):
    with open(st_c.change_hotspot_file, "w") as html_file:
        html_file.write(f'{st_c.html_doctype}')
        html_file.write('<style>')
        html_file.write(f'{st_c.header_css}')
        html_file.write('p { text-align: left ; }')
        html_file.write('li { text-align: left ; color: red ; }')
        html_file.write('</style></head>')
        html_file.write('<title>Change hotspot name</title><body><h1>Change hotspot name</h1> <form action="" method="post" enctype="text/html" novalidate>')
        if errors:
            html_line = '<ul>'
            for error in errors:
                html_line += f'<li>{error}</li>'
            html_line += '</ul>'
            html_file.write(html_line)

        html_file.write('<p>Please enter a new name for the builtin WiFi or just press "save" to continue</p>')
        html_file.write(f'<p><label for="hot_name">Name for builtin WiFi</label> <input type="text" name="hot_name" id="hot_name" value="{ssid}"/></p>')
        html_file.write('<p>When you press "Save" the unit will restart, please reconnect to the new name</p>')
        html_file.write('<p><button type="submit" name="save" value="save">Save</button></p></form></body>')

def render_configured_wifi(ssid, ip, mac, errors=None):
    with open(st_c.configured_wifi_html_file, "w") as html_file:
        html_file.write(f'{st_c.html_doctype}')
        html_file.write('<style>')
        html_file.write(f'{st_c.header_css}')
        html_file.write('p { text-align: left ; }')
        html_file.write('</style></head>')
        if errors:
            html_file.write('<title>Connection Failure</title><body><h1>Connection Failure</h1><form action="" method="post" enctype="text/html" novalidate>')
            html_file.write('<p>This error occurred:<br>')
            for err in errors:
                html_file.write(f"{err}<br>")
            html_file.write('Reboot to try again.</p> <p><button type="submit" name="reboot" value="reboot">Reboot</button></p> </form> </body> </html>')
        else:
            html_file.write('<title>Wifi Configured</title><body><h1>Wifi Configured</h1><form action="" method="post" enctype="text/html" novalidate>')
            html_file.write(f'<p>Successfully connected to "{ssid}" wireless network and received this IP<br><b>{ip}</b>')
            html_file.write(f'<p><b>Record this IP</b> and use it to connect to this station on the {ssid} network<br> If you are unable to connect, look for the IP address associated with this MAC address<br> <b>{mac}</b><br> After pressing "Reboot", wait a few seconds then try to connect on the {ssid} network</p> <p><button type="submit" name="reboot" value="reboot">Reboot</button></p> </form> </body> </html>')

def render_configure_wifi(wifi_json, errors=None):
    preferred_ip = wifi_json["preferred_ip"]
    wifi_pass = wifi_json["wifi_pass"]
    with open(st_c.configure_wifi_html_file, "w") as html_file:
        html_file.write(f'{st_c.html_doctype}')
        html_file.write('<style>')
        html_file.write(f'{st_c.header_css}')
        html_file.write('p { text-align: left ; }')
        html_file.write('li { text-align: left ; color: red ; }')
        html_file.write('.blue_text { color: blue; }')
        html_file.write('</style></head>')
        html_file.write('<title>Wifi Configuration</title><body><h1>Configure WiFi access</h1> <form action="" method="post" enctype="text/html" novalidate>')
        if st_c.wifi_warnings and wifi_json["warn"]:
            html_line = '<p><span class="blue_text">'
            for item in wifi_json["warn"]:
                html_line += f'{item}<br>'
            html_line += '</span></p>'
            html_file.write(html_line)

        if errors:
            html_line = '<ul>'
            for error in errors:
                html_line += f'<li>{error}</li>'
            html_line += '</ul>'
            html_file.write(html_line)

        html_file.write('<p><label for="ssids">Choose a WiFi network </label>')
        html_file.write('<select font-size=medium name="ssid" id="ssid">\n')
        for ssid in wifi_json["access_points"]:
            html_file.write(f'<option font-size=medium value="{ssid}">{ssid}</option>\n')
        html_file.write('</select></p>\n')
        html_file.write(f'<p>Password for WiFi network <input type="text" minlength="8" maxlength="16" size="16" name="wifi_pass" value="{wifi_pass}" /></p>\n')
        html_file.write('<p>If you leave the preferred IP blank or 0, the system will use the IP provided by the router which means it might change unexpectedly.</p>\n')
        html_file.write(f'<p>Preferred IP <input type="number" minlength="3" maxlength="3" size="3" name="preferred_ip" value="{preferred_ip}" /></p>\n')
        html_file.write('<p>After saving reconnect to the hotspot and refresh</p>')
        html_file.write('<p><button type="submit" name="save" value="save">Save</button><button type="cancel" name="quit" value="quit">Quit</button></p></form></body>')
