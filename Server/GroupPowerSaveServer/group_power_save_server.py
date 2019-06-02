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
        self.non_member_id_set = set()
        self.group_dict_lock = Lock()
        self.group_dict = {}

        for thread in self.threads:
            thread.start()

        web.run_app(self.app)

    def __duty_cycle_tick(self, interval: int):
        leader_update_interval = 10
        while(True):
            # role update
            with self.group_dict_lock:
                for group in self.group_dict.values():
                    if group.is_need_leader_update(leader_update_interval):
                        self.user_dict[group.next_leader_id].reserve_status_change(UserStatus.GROUP_LEADER)

            # TODO duty cycle for group validation / remove non-active user

            time.sleep(interval)

    def __group_match_tick(self, interval: int):
        while(True):
            # TODO group matching for non-grouped user
            # 1 : dbscan algorithm + gps based movement vector alignment
            # 2 : acceleration
            
            # temporal : manual grouping 
            if len(self.non_member_id_set) is not 0:
                group = Group(list(self.non_member_id_set))
                with self.group_dict_lock:
                    self.group_dict[group.id] = group

                for id in self.non_member_id_set:
                    if id == group.current_leader_id:
                        role = UserStatus.GROUP_LEADER
                    else:
                        role = UserStatus.GROUP_MEMBER
                    self.user_dict[id].reserve_status_change(role, group.id)

                self.non_member_id_set.clear()
                
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
                    return False, "Doesn't contain : " + "".join(str(x) + " " for x in not_available_list)

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
                return web.Response(status=422, text="Duplicate id detected : "+str(id))
            with self.user_dict_lock:
                self.user_dict[id] = User(id)
                self.non_member_id_set.add(id)
                print("New Client Registered : ", str(id))
            return web.Response()
        else:
            return web.Response(status=422, text=result)

    async def __put__data_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")

        succeess, result = await self.__parse_json(request, ["time"])
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
                "gps" : user.gps,
                "acceleration" : user.acceleration,
                # TODO : more informations (gps position ...)
            }
        )
    
    async def __ping_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")
        
        pending_status = self.user_dict[id].get_pending_status()

        # update leader the group
        # TODO : missing responde delivery check
        if pending_status is UserStatus.GROUP_LEADER:
            group = self.group_dict[self.user_dict[id].group_id]
            if group.current_leader_id != id:
                self.user_dict[group.current_leader_id].reserve_status_change(UserStatus.GROUP_MEMBER)
                group.confirm_leader_update(id)

        # let client know about a new role
        if pending_status is not None:
            print("User", id, "has changed to", pending_status)
            return web.json_response({"status" : pending_status.value })
  
        return web.Response()
