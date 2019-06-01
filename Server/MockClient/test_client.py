import argparse

import asyncio
import aiohttp

import sys
import random
import numpy as np
from functools import partial

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

class ClientSet(object):
    def __init__(self, initialize_logic):
        self.clients = initialize_logic()
    
    async def register(self, session, target_address):
        for client in self.clients:
            resp = await session.post(target_address + "register", json={'id' : client.id})
            
            # reassign randomly generated id
            if resp.status == 422:
                success = False
                while success is False:
                    random_id = random.randint(0, sys.maxsize)
                    resp = await session.post(target_address + "register", json={'id' : random_id})
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

async def register(session, target_address, center, num_client):
    def random_init(center, num_client):
        clients = []
        for i in range(num_client):
            clients.append(Client(np.add(center, [random.uniform(0, 0.01),random.uniform(0, 0.01)])))
        return clients

    clientSet = ClientSet(partial(random_init, center, num_client))
    return await clientSet.register(session, target_address)

async def main(loop):
    map_center = [37.4556699,126.9533264]
    clients = 10
    target_address = "http://localhost:8080/"

    async with aiohttp.ClientSession(loop=loop) as session:
        result = await register(session, target_address, map_center, clients)
        print("Registration result : ", str(result))
        if result is True:
            pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()