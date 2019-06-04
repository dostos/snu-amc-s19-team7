import argparse
import asyncio
import aiohttp
import sys, inspect
import random
import numpy as np
import time

from enum import Enum
from functools import partial
from threading import Thread, Lock
from datetime import datetime

sys.path.append("..")
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
        self.status = UserStatus.NON_GROUP_MEMBER

class DefaultTest(object):
    def __init__(self, session, target_address, center, num_client):
        self.session = session
        self.target_address = target_address
        self.center = center

        self.__generate_clients(num_client)
        
    
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

    async def non_member_tick(self, interval):
        pass

    async def ping_tick(self, ping_interval):
        pass

    async def update_callback(self, callback, interval):
        if callback is not None:
            while(True):
                callback(self.clients)
                await asyncio.sleep(interval)

    # virtual function for client initialization
    def __generate_clients(self, num_client):
        self.clients = []
        for i in range(num_client):
            self.clients.append(Client(np.add(self.center, [random.uniform(0, 0.01),random.uniform(0, 0.01)])))

class RoleUpdateTest(DefaultTest):
    async def __ping(self, client):
        # simulate random network fluctuation
        async with self.session.get(self.target_address + "ping", params={'id' : client.id}) as resp:
            if resp.content_type == 'application/json':
                json = await resp.json()
                client.status = UserStatus(json["status"])

    async def ping_tick(self, ping_interval):
        while(True):
            for client in self.clients:
                asyncio.ensure_future(self.__ping(client))
            await asyncio.sleep(ping_interval)
    
# TODO : Position get (client side loop)
# Position update (server side) - non member
# Position update (server side) - leader / distribute to members
# Offset computation in a group matching stage
# Network fluctuation simulation
class PositionUpdateTest(RoleUpdateTest):
    async def __non_member_update(self, client):
        pass
    
    async def non_member_tick(self, interval):
        while(True):
            for client in self.clients:
                asyncio.ensure_future(self.__non_member_update(client))
            await asyncio.sleep(interval)

async def execute(loop, test_type, clients, target_address, callback = None):
    map_center = [37.4556699,126.9533264]

    async with aiohttp.ClientSession() as session:
        test = test_type(session, target_address, map_center, clients)
        initialized = await test.register()
        print("Registration result : ", initialized)
        if initialized:
            # add all update functions here
            await asyncio.gather(
                test.ping_tick(2), 
                test.update_callback(callback, 0.5),
                test.non_member_tick(3), 
                loop=loop)