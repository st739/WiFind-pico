'''
basic config file to cater for startup
initialisation
wifi setup
'''

config_dirs = ('w_templates', '.secrets', 'data')

w_template_path = "/w_templates"
configure_wifi_html_file = f"{w_template_path}/configure.html"
configured_wifi_html_file = f"{w_template_path}/configured.html"
change_hotspot_file = f"{w_template_path}/change_hot.html"

secrets_path = "/.secrets"
wifi_json_file = f"{secrets_path}/wifi.json"
ap_status_file = f"{secrets_path}/status"
ap_kill_file = f"{secrets_path}/kill"
ap_start_file = f"{secrets_path}/start"

# This directory could be used in app config too
data_path = "/data"
error_file = f"{data_path}/error.file"

# for ssid scanning and configuration
scan_count = 6
# for exclusion of ssids based on rssi
# warn about stations with rssi less than this
signal_poor = -75
# drop stations with rssi less than this
signal_limit = -80
# low and high limits for preferred_ip
wifi_static_ip = { 'low' : 100, 'high' : 250 }
hotspot_name = 'Hotspot'
# number of reboots in access point mode without setting time
kill_count = 3
# number of attempts to connect to wifi
wifi_max_attempts = 3
# display wifi warnings
wifi_warnings = False

header_css = "html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;} .container { max-width: 600px; padding: 5px 20px 5px 0px; } .subcontainer { background-color: white; float: left; border: 2px solid #dcdcdc; padding: 5px 10px 5px 5px; border-radius: 10px; text-align: center; font-family: 'Helvetica', sans-serif; } a { color: royalblue; text-decoration: none; font-weight: bold; } a:visited { color: purple; text-decoration: none; } .cleared { clear: left; } "
html_doctype = "<!DOCTYPE html> <head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><meta http-equiv=\"Cache-Control\" content=\"no-cache, no-store, must-revalidate\"> <meta http-equiv=\"Pragma\" content=\"no-cache\"> <meta http-equiv=\"Expires\" content=\"0\">"
