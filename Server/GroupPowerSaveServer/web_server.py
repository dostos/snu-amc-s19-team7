from aiohttp import web

async def hello(request):
    return web.Response(text="Hello, world")

class WebServer(object):
    def __init__(self):
        self.app = web.Application()
        #TODO register handlers
        self.app.add_routes([web.get('/', hello)])
        web.run_app(self.app)

    def terminate(self):
        pass

    # TODO base tick for position update / sending
    def __tick(self, tick_time):
        pass

    # TODO duty cycle for group validation
    def __duty_cycle_tick(self, tick_time):
        pass

    # TODO group matching for non-grouped users
    def __group_match_tick(self, tick_time):
        pass

    async def __register_handler(self, user):
        pass

    async def __data_handler(self, user):
        pass