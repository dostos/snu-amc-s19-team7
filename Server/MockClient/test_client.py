import argparse

import asyncio
import aiohttp

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
        resp_count = len(self.clients)
        success_count = 0
        for client in self.clients:
            async with session.post(target_address + "register", json={'id' : client.id}) as resp:
                resp_count -= 1
                
                if resp.status == 200:
                    success_count += 1
                else:
                    print(await resp.text())

                if resp_count is 0:
                    print("Register completed result : ", success_count, "/", len(self.clients))

async def test_register(session, target_address, center, num_client):
    def random_init(center, num_client):
        clients = []
        for i in range(num_client):
            clients.append(Client(np.add(center, [random.uniform(0, 0.01),random.uniform(0, 0.01)])))
        return clients

    clientSet = ClientSet(partial(random_init, center, num_client))
    await clientSet.register(session, target_address)

async def main(loop):
    map_center = [37.4556699,126.9533264]
    clients = 10
    target_address = "http://localhost:8080/"

    async with aiohttp.ClientSession(loop=loop) as session:
        await test_register(session, target_address, map_center, clients)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()