from aiohttp import web
from threading import Thread, Lock
import time
import json

from .group import Group
from .user import User, UserStatus
from .data_visualizer import data_to_html
# TODO : SSL / security logic ?                          

class GroupPowerSaveServer(object):
    def __init__(self):
        self.app = web.Application()
        #TODO register more handlers
        self.app.add_routes([web.get("/", self.__index_handler)])
        self.app.add_routes([web.post('/register', self.__register_handler)])
        self.app.add_routes([web.put('/user-data', self.__put__data_handler)])
        self.app.add_routes([web.get("/user-data",self.__get_data_handler)])
        self.app.add_routes([web.get("/ping",self.__ping_handler)]) 

        # Worker threads setup
        self.threads = []
        self.threads.append(Thread(target=self.__duty_cycle_tick, args=[5]))
        self.threads.append(Thread(target=self.__group_match_tick, args=[3]))

        self.user_dict_lock = Lock()
        self.user_dict = {}
        self.group_dict_lock = Lock()
        id = Group.get_unique_id()
        # temporal manual grouping
        self.global_group = Group(id)
        self.group_dict = { id: self.global_group }

        for thread in self.threads:
            thread.start()

        web.run_app(self.app)

    def __duty_cycle_tick(self, interval: int):
        while(True):
            # TODO duty cycle for group validation / remove non-active user, leader
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
    
    async def __index_handler(self, request: web.Request) -> web.Response:
        with self.user_dict_lock and self.group_dict_lock:
            return web.Response(content_type="html", body=data_to_html(self.user_dict, self.group_dict))


    async def __register_handler(self, request: web.Request) -> web.Response:
        succeess, result = await self.__parse_json(request, ["id"])

        if succeess:
            id = str(result["id"])
            if id in self.user_dict:
                return web.Response(status=422, text="Duplicate id detected")
            with self.user_dict_lock:
                self.user_dict[id] = User(id)
                # temporal : manual grouping
                self.user_dict[id].reserve_status_change(UserStatus.GROUP_MEMBER, self.global_group.id)
                print(self.user_dict)
            return web.Response()
        else:
            return web.Response(status=422, text=result)

    async def __put__data_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")

        succeess, result = await self.__parse_json(request)
        if succeess:
            user = self.user_dict[id]
            user.update_data(result)
            print("trying to put data from ", id, " ", result)
            return web.Response()
        else:
            return web.Response(status=422, text=result)


    async def __get_data_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")
        
        user = self.user_dict[id]

        return web.json_response(
            {
                "id" : user.id,
                "group_id" : user.group_id,
                "status" : user.status.value,
                "data" : user.data
                # TODO : more informations (gps position ...)
            }
        )
    
    async def __ping_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")
        
        pending_status = self.user_dict[id].try_update_status()
        if pending_status is not UserStatus.NONE:
            return web.json_response({"status" : pending_status.value })

        # TODO : response  
        return web.Response()
