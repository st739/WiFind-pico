'''
stub to demo start an application
'''
import asyncio
from microdot.microdot import Microdot

async def run_webserver():
    app = Microdot()
    @app.route("/", methods=["GET","POST"])
    def index(request):
        return 'Hello, world!'

    app.run(port=80)

async def start_app():
    await asyncio.gather(run_webserver())
