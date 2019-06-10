from enum import Enum
import numpy as np
import math

# gps positions -> distance in meters
def get_distance(pos1, pos2) :  
    R = 6378.137 # Radius of earth in KM
    dLat = pos2[0] * math.pi / 180 - pos1[0] * math.pi / 180
    dLon = pos2[1] * math.pi / 180 - pos1[1] * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(pos1[0] * math.pi / 180) * math.cos(pos2[0] * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000

class UserStatus(Enum):
    NONE = -1
    NON_GROUP_MEMBER = 0
    GROUP_MEMBER = 1
    GROUP_LEADER = 2

class User(object):
    def __init__(self, id):
        self._id = id
        self._group_id = None
        self._status = UserStatus.NON_GROUP_MEMBER
        self._pending_status_change = UserStatus.NONE
        self._pending_group_id = None
        self._gps = []
        self._acceleration = []
        self._offset = None
        self._need_acceleration = False
        self._need_exit = False

    def update_data_from_leader(self, leader):
        if self._offset is not None:
            leader_data = np.add(leader.gps[-1], [0, self._offset[0], self._offset[1]])
            self._gps.append(leader_data)

    def update_data(self, data):
        # Need lock here?
        if 'time' in data and 'magnitude' in data:
            self._need_acceleration = False
            self._acceleration = [data['time'], data['magnitude']]
            print("Got acceleration of", self._id)
            print("Got acceleration", self._acceleration)
        elif 'time' in data and 'latitude' in data and 'longitude' in data:
            if self._status is UserStatus.GROUP_MEMBER:
                if get_distance([data['latitude'], data['longitude']], self.gps[-1][1:3]) > 20:
                    self._need_exit = True
            self._gps.append([data['time'], data['latitude'], data['longitude']])
    
    def request_acceleration(self):
        self._need_acceleration = True
    
    @property
    def need_exit(self):
        return self._need_exit

    @property
    def need_acceleration(self):
        return self._need_acceleration

    @property
    def gps(self):
        return self._gps

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def id(self):
        return self._id

    @property
    def group_id(self):
        return self._group_id

    @property
    def status(self) -> UserStatus:
        return self._status

    def update_offset(self, leader):
        self._offset = np.subtract(self.gps[-1][1:],leader.gps[-1][1:]) 

    def reserve_status_change(self, status : UserStatus, group_id : int = None):
        """
        reserve status change for next ping
        """
        if self._status is not status:
            self._pending_status_change = status
            if group_id is not None:
                self._group_id = group_id
    
    def reset_group(self):
        self._need_exit = False
        self._pending_status_change = UserStatus.NON_GROUP_MEMBER
        self._group_id = None
    
    def get_pending_status(self):
        """
        try to get pending status if there is any change
        """
        pending_status = self._pending_status_change
        self._pending_status_change = UserStatus.NONE
        if self._status is not pending_status and pending_status is not UserStatus.NONE:
            self._status = pending_status
                
            return pending_status
        else:
            return None