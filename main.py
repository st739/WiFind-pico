'''
generic code to initialise wifi connection then start arbitrary application
'''
import os
import asyncio
from application import start_app
import startup_cfg as st_c
from start_wifi import start_wifi

def init_dirs(dirs):
    for d in dirs:
        try:
            if os.stat(d)[0] & 0x4000:
                pass
        except OSError:
            os.mkdir(d)

init_dirs(st_c.config_dirs)
wifi_type = start_wifi() # STATION, ACCESS_POINT or None
wifi_type and asyncio.run(start_app(wifi_type))
