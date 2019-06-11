import argparse
import asyncio
import aiohttp
import sys, inspect
import random
import numpy as np
import time
import math
import functools

from enum import Enum, auto
from functools import partial
from threading import Thread, Lock
from datetime import datetime

sys.path.append("..")
from GroupPowerSaveServer.user import UserStatus

# gps positions -> distance in meters
def get_distance(pos1, pos2) :  
    R = 6378.137 # Radius of earth in KM
    dLat = pos2[0] * math.pi / 180 - pos1[0] * math.pi / 180
    dLon = pos2[1] * math.pi / 180 - pos1[1] * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(pos1[0] * math.pi / 180) * math.cos(pos2[0] * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000

# Assuming that all points are on the same line
def calculate_t(current_pos, pos1, pos2):
    d_total = get_distance(pos1, pos2)
    d_0 = get_distance(pos1, current_pos)
    return d_0 / d_total

def interpolate(t, pos1, pos2):
    return np.add(np.multiply(pos1, 1 - t), np.multiply(pos2, t))

class ClientStatus(Enum):
    WANDER = auto(),
    WAIT_BUS = auto(),
    ON_BUS = auto()

class Bus(object):
    def __init__(self, route, route_index, index, speed):
        self.route = route
        self.route_index = route_index
        self.index = index
        self.speed = speed
        self._t = 0
        self._dt = self.speed / get_distance(self.route[self.index], self.route[self.next_index])
        self._stop_count = 0
    
    @property
    def position(self):
        return interpolate(self._t, self.route[self.index], self.route[self.next_index])
    
    @property
    def next_index(self) -> int:
        next_index = self.index + 1
        if next_index == len(self.route):
            return 0
        else:
            return next_index
    
    @property
    def is_stop(self):
        return self._stop_count > 0

    def tick(self):
        if self.is_stop:
            self._stop_count -= 1
        else:
            self._t += self._dt
            # arrived
            if self._t >= 1:
                self.index = self.next_index
                self._t = 0
                self._dt = self.speed / get_distance(self.route[self.index], self.route[self.next_index])
                self._stop_count = np.random.randint(3,5)

class Client(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def get_unique_id():
        id = Client.unique_id_count
        Client.unique_id_count +=1
        return id

    def __init__(self, position, speed, route, route_index):
        self.id = Client.get_unique_id()
        self.position_from_server = None
        self.group_id = None
        self.status = UserStatus.NON_GROUP_MEMBER
        self.local_status = ClientStatus.WANDER
        self.gps_request_count = 0
        self.speed = speed
        self.route = route
        self.route_index = route_index

        self._t = 0
        self._dt = 1
        self._current_position = position
        self._next_position = position
        self._stop_index = None
        self._bus = None
        self._bus_offset = [random.uniform(-0.0005, 0.0005), random.uniform(-0.0005, 0.0005)]
    
    @property
    def position(self):
        if self.local_status is ClientStatus.ON_BUS:
            return np.add(self._bus.position, self._bus_offset)
        else:
            return interpolate(self._t, self._current_position, self._next_position)

    def tick(self, buses):
        if self.local_status is ClientStatus.WANDER:
            self._t += self._dt

            # arrived
            if self._t >= 1:
                random_action = random.random()
                if random_action < 0.90:
                    self._current_position = self._next_position
                    self._next_position = np.add(self._current_position, [random.uniform(-0.001, 0.001), random.uniform(-0.001, 0.001)])
                else:
                    closest_stop_index = None
                    closest_stop_distance = sys.maxsize

                    for i in range(len(self.route)):
                        distance = get_distance(self._current_position, self.route[i])
                        if distance < closest_stop_distance:
                            closest_stop_distance = distance
                            closest_stop_index = i

                    self._next_position = self.route[closest_stop_index]
                    self._stop_index = closest_stop_index
                    self.local_status = ClientStatus.WAIT_BUS

                self._t = 0
                self._dt = self.speed / get_distance(self._current_position, self._next_position)
        
        elif self.local_status is ClientStatus.WAIT_BUS:
            self._t += self._dt

            if self._t >= 1:
                self._t = 1

                bus : Bus
                for bus in buses:
                    if bus.is_stop and bus.route_index == self.route_index and bus.index == self._stop_index:
                        self.local_status = ClientStatus.ON_BUS
                        self._bus = bus
        elif self.local_status is ClientStatus.ON_BUS:
            random_action = random.random()
            bus : Bus
            for bus in buses:
                if bus.is_stop and bus.route_index == self.route_index and bus.index == self._stop_index:
                    if random_action > 0.5:
                        self.local_status = ClientStatus.WANDER
                        break


class DefaultTest(object):
    def __init__(self, session, target_address, map_bound, bus_per_route, routes, num_client):
        self.session = session
        self.target_address = target_address
        self.map_bound = map_bound
        self.routes = routes

        self.clients = []
        for _ in range(num_client):
            random_route_index = random.randint(0, len(self.routes) - 1)
            self.clients.append(Client([random.uniform(self.map_bound[0][0], self.map_bound[1][0]), random.uniform(self.map_bound[0][1], self.map_bound[1][1])], 10, self.routes[random_route_index], random_route_index))

        self.buses = []
        for route_index in range(len(routes)):
            for i in range(bus_per_route):
                self.buses.append(Bus(routes[route_index], route_index, int(len(routes[route_index]) / bus_per_route * i) , 30))
        
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

    async def gps_get_tick(self, interval):
        pass
        
    async def gps_set_tick(self, status, interval):
        pass

    async def ping_tick(self, ping_interval):
        pass
    
    def update_tick(self):
        pass

    async def update_callback(self, callback, interval):
        while(True):
            if self.session.closed:
                break
            self.update_tick()
            if callback is not None:
                callback(self.clients, self.buses)
            await asyncio.sleep(interval)

class RoleUpdateTest(DefaultTest):
    async def __ping(self, client):
        # simulate random network fluctuation
        async with self.session.get(self.target_address + "ping", params={'id' : client.id}) as resp:
            if resp.content_type == 'application/json':
                json = await resp.json()
                if "status" in json:
                    client.status = UserStatus(json["status"])
                if "group_id" in json:
                    client.group_id = json["group_id"]
                if "need_acceleration" in json and json["need_acceleration"] is True:
                    print("Client need acceleration", json["need_acceleration"])

    async def ping_tick(self, ping_interval):
        while(True):
            if self.session.closed:
                break
            for client in self.clients:
                asyncio.ensure_future(self.__ping(client))
            await asyncio.sleep(ping_interval)
    
# TODO :
# Network fluctuation simulation
class PositionUpdateTest(RoleUpdateTest):
    def update_tick(self):
        for bus in self.buses:
            bus.tick()

        for client in self.clients:
            client.tick(self.buses)

    async def __set_position(self, client : Client):
        async with self.session.put(
            self.target_address + "user-data", 
            params={'id' : client.id}, 
            json={
                'time' : datetime.now().microsecond,
                'latitude' : client.position[0],
                'longitude' : client.position[1] }): 
            client.gps_request_count += 1

    async def gps_set_tick(self, status, interval):
        while(True):
            if self.session.closed:
                break
            for client in self.clients:
                if client.status is status:
                    asyncio.ensure_future(self.__set_position(client))
            await asyncio.sleep(interval)

    async def __get_position(self, client :Client):
        async with self.session.get(self.target_address + "user-data", params={'id' : client.id}) as resp:
            if resp.content_type == 'application/json':
                json = await resp.json()
                if "latitude" in json and "longitude" in json:
                    client.position_from_server = [json["latitude"], json["longitude"]]
                    
    async def gps_get_tick(self, interval):
        while(True):
            if self.session.closed:
                break
            for client in self.clients:
                asyncio.ensure_future(self.__get_position(client))
            await asyncio.sleep(interval)

async def execute(loop, test_type, clients, target_address, map_bound = None, bus_per_route = 1, routes = None, callback = None):
    if map_bound is None:
        map_center = [37.4556699,126.9533264]
        map_bound = [np.add(map_center, -0.005), np.add(map_center, +0.005)]
    
    if routes is None:
        routes = [
            [np.add(map_center, random.uniform(-0.005, 0.005)),
            np.add(map_center, random.uniform(-0.005, 0.005)),
            np.add(map_center, random.uniform(-0.005, 0.005))]]
        
    async with aiohttp.ClientSession(loop=loop) as session:
        test = test_type(session, target_address, map_bound, bus_per_route, routes, clients)
        initialized = await test.register()
        print("Registration result : ", initialized)
        if initialized:
            # add all update functions here
            await asyncio.gather(
                test.ping_tick(10), 
                test.update_callback(callback, 0.5),
                test.gps_set_tick(UserStatus.NON_GROUP_MEMBER, 1),
                test.gps_set_tick(UserStatus.GROUP_MEMBER, 5),
                test.gps_set_tick(UserStatus.GROUP_LEADER, 0.5),
                test.gps_get_tick(0.5), 
                loop=loop)