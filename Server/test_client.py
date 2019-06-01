import argparse

import asyncio
import aiohttp

import sys
import random
import numpy as np
from functools import partial
from GroupPowerSaveServer.user import UserStatus

class Client(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def get_unique_id():
        id = Client.unique_id_count
        Client.unique_id_count +=1
        return id

    def __init__(self, position):
        self.id = Client.get_unique_id()
        self.position = position

class DefaultTest(object):
    def __init__(self, session, target_address, center, num_client):
        self.session = session
        self.target_address = target_address
        self.center = center

        self._generate_clients(num_client)
        
    
    async def register(self):
        for client in self.clients:
            resp = await self.session.post(self.target_address + "register", json={'id' : client.id})
            
            # reassign randomly generated id
            if resp.status == 422:
                success = False
                while success is False:
                    random_id = random.randint(0, sys.maxsize)
                    resp = await self.session.post(self.target_address + "register", json={'id' : random_id})
                    # success?
                    success = resp.status == 200
                    if success:
                        client.id = random_id
                    # somehow server is gone 
                    elif resp.status != 422:
                        return False
            # network related error cannot be fixed
            elif resp.status != 200:
                return False
        return True
    
    def loop(self):
        # TODO : default loops (ping)
        pass

    # virtual function for client initialization
    def _generate_clients(self, num_client):
        self.clients = []
        for i in range(num_client):
            self.clients.append(Client(np.add(self.center, [random.uniform(0, 0.01),random.uniform(0, 0.01)])))


async def main(loop):
    map_center = [37.4556699,126.9533264]
    clients = 10
    target_address = "http://localhost:8080/"

    async with aiohttp.ClientSession(loop=loop) as session:
        test = DefaultTest(session, target_address, map_center, clients)
        initialized = await test.register()
        print("Registration result : ", initialized)
        if initialized:
            pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()