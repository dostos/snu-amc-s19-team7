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

    def __init__(self):
        self.id = Group.__get_unique_id()
        self.member_ids = {}

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

    def __duty_cycle_tick(self, interval):
        while(True):
            # TODO duty cycle for group validation
            time.sleep(interval)

    def __group_match_tick(self, interval):
        while(True):
            # TODO group matching for non-grouped users
            time.sleep(interval)

    async def __register_handler(self, request):
        #data = await request.json()
        # TODO : Get unique identification from a user to prevent multiple registration
        try:
            if request.can_read_body:
                print(await request.json())
        except ValueError:
            print("Not able to parse json")
        
        with self.user_dict_lock:
            # temporal id generation
            current_id = self.unique_user_id_count
            self.unique_user_id_count += 1
            print("User registered id : ", current_id)
            self.user_dict[current_id] = User(current_id)

        return web.Response(text=str(current_id))

    async def __put__data_handler(self, request):
        if request.can_read_body:
            print(await request.json())
        return web.Response()

    async def __get_data_handler(self, request):
        data = await request.json()
        print(data)
        return web.Response()

server = GroupPowwerSaveServer()
