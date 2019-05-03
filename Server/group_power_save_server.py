from aiohttp import web
from threading import Thread, Lock
import time

# TODO : SSL / security logic ?

class Group(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def __get_unique_id():
        id = Group.unique_id_count
        Group.unique_id_count +=1
        return id

    def __init__(self, member_id_list : list):
        self.id = Group.__get_unique_id()
        self.member_id_list = member_id_list

class User(object):
    def __init__(self, id):
        self.id = id

    def update_data(self, data):
        # TODO : store latitude / longitude / accel data
        pass

class GroupPowerSaveServer(object):
    def __init__(self):
        self.app = web.Application()
        #TODO register more handlers
        self.app.add_routes([web.post('/register', self.__register_handler)])
        self.app.add_routes([web.put('/user-data', self.__put__data_handler)])
        self.app.add_routes([web.get("/user-data",self.__get_data_handler)])
        self.app.add_routes([web.get("/ping",self.__ping_handler)])
        self.unique_user_id_count = 0

        # Worker threads setup
        self.threads = []
        self.threads.append(Thread(target=self.__duty_cycle_tick, args=[5]))
        self.threads.append(Thread(target=self.__group_match_tick, args=[3]))

        self.user_dict_lock = Lock()
        self.user_dict = {}
        self.group_dict_lock = Lock()
        self.group_dict = {}

        for thread in self.threads:
            thread.start()

        web.run_app(self.app)

    def __duty_cycle_tick(self, interval: int):
        while(True):
            # TODO duty cycle for group validation
            time.sleep(interval)

    def __group_match_tick(self, interval: int):
        while(True):
            # TODO group matching for non-grouped users
            time.sleep(interval)

    async def __parse_json(self, request: web.Request, must_contains : list = []):    
        """
        parse json file from request\n
        :param request: http request\n
        :param must_contains: list of keys that json must contain\n
        :return: bool (success), json object or error msg
        """
        try:
            if request.can_read_body:
                json = await request.json()
                not_available_list = []
                for key in must_contains:
                    if key not in json:
                        not_available_list.append(key)
                
                if len(not_available_list) == 0:
                    return True, json
                else:
                    return False, "Doesn't contain : " + "".join(str(x) for x in not_available_list)

        except ValueError:
            return False, "Not able to parse json"



    async def __register_handler(self, request: web.Request) -> web.Response:
        succeess, result = await self.__parse_json(request, ["id"])

        if succeess:
            if result["id"] in self.user_dict:
                return web.Response(status=422, text="Duplicate id detected")
            with self.user_dict_lock:
                self.user_dict[result["id"]] = User(result["id"])
                print(self.user_dict)
            return web.Response()
        else:
            return web.Response(status=422, text=result)

    async def __put__data_handler(self, request: web.Request) -> web.Response:
        if request.can_read_body:
            print(await request.json())
        return web.Response()

    async def __get_data_handler(self, request: web.Request) -> web.Response:
        data = await request.json()
        print(data)
        return web.Response()
    
    async def __ping_handler(self, request: web.Request) -> web.Response:
        succeess, result = await self.__parse_json(request, ["id"])

        if succeess:
            # TODO : response  
            return web.Response()
        else:
            return web.Response(status=422, text=result)

server = GroupPowerSaveServer()
