'''
stub to demo start an application
could import startup_cfg as st_c
then after the time is set (assuming the app requires the time)
or after the app is running
open(st_c.ap_start_file, "w").close()
to allow the killswitch to function in a sensible way

'''
import asyncio
from external.microdot import Microdot

async def run_webserver(wifi_type):
    app = Microdot()
    @app.route("/", methods=["GET","POST"])
    def index(request):
        return f'Hello, world in {wifi_type} mode!'

    app.run(port=80)

async def start_app(wifi_type):
    # wifi_type is STATION or ACCESS_POINT
    # if the application behaves differently depending on type,
    # cater for it here or pass wifi_type to the application
    await asyncio.gather(run_webserver(wifi_type))
