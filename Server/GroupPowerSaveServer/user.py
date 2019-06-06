from enum import Enum
import numpy as np

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
    def ping(self):
        # reset ping timer for connection check
        pass

    def update_data(self, data):
        # TODO : store latitude / longitude / accel data
        # Need lock here?
        if 'time' in data and 'latitude' in data and 'longitude' in data:
            # ignore outdated data
            if len(self._gps) == 0 or self._gps[-1][0] < data['time']:
                self._gps.append([data['time'], data['latitude'], data['longitude']])
        elif 'acceleration' in data:
            self._acceleration = data['acceleration']

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

    def reserve_status_change(self, status : UserStatus, group_id : int = None):
        """
        reserve status change for next ping
        """
        if self._status is not status:
            self._pending_status_change = status
            if group_id is not None:
                self._pending_group_id = group_id
    
    def get_pending_status(self):
        """
        try to get pending status if there is any change
        """
        pending_status = self._pending_status_change
        self._pending_status_change = UserStatus.NONE
        if self._status is not pending_status and pending_status is not UserStatus.NONE:
            self._status = pending_status
            
            if self._pending_group_id is not None:
                self._group_id = self._pending_group_id
                self._pending_group_id = None
                
            return pending_status
        else:
            return None