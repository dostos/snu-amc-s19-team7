from enum import Enum

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
        self._data = None

    def ping(self):
        # reset ping timer for connection check
        pass

    def update_data(self, data):
        # TODO : store latitude / longitude / accel data
        # Need lock here?
        self._data = data

    @property
    def data(self):
        return self._data

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
    
    def try_update_status(self):
        """
        try update status if there is any change
        """
        pending_status = self._pending_status_change
        self._pending_status_change = UserStatus.NONE
        if self._status is not pending_status and pending_status is not UserStatus.NONE:
            self._status = pending_status
            print("User ", self._id, " is a ", self._status.name)
            
            if self._pending_group_id is not None:
                self._group_id = self._pending_group_id
                self._pending_group_id = None
                
            return pending_status
        else:
            return UserStatus.NONE