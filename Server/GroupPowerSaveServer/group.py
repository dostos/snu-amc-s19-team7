from threading import Lock
import time
from datetime import datetime

class Group(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def __get_unique_id():
        id = Group.unique_id_count
        Group.unique_id_count +=1
        return id

    def __init__(self, member_id_list : list = []):
        self._id = Group.__get_unique_id()
        self.member_id_list = member_id_list
        self._member_id_list_lock = Lock()
        self._leader_index = 0
        self._last_update_time = datetime.now()
        self._need_leader_update = False

    def add_member(self, id):
        with self._member_id_list_lock:
            self.member_id_list.add(id)

    def remove_member(self, id):
        with self._member_id_list_lock:
            current_leader = self.current_leader_id
            self.member_id_list.remove(id)
            if current_leader == id:
                self._need_leader_update = True
            # update leader index 
            else:
                self._leader_index = self.member_id_list.index(current_leader)

    def is_need_leader_update(self, interval_in_second):
        if self._need_leader_update is True:
            self._need_leader_update = False
            return True
        if len(self.member_id_list) == 0:
            return False
        elapsed = datetime.now() - self._last_update_time
        return elapsed.seconds >= interval_in_second


    def confirm_leader_update(self, id):
        next_index = self.__next_leader_index()
        if self.member_id_list[self.__next_leader_index()] == id:
            self._leader_index = next_index
            self._last_update_time = datetime.now()
    
    def __next_leader_index(self):
        with self._member_id_list_lock:
            next_index = self._leader_index + 1
            if next_index == len(self.member_id_list):
                next_index = 0
        return next_index

    @property
    def current_leader_id(self):
        return self.member_id_list[self._leader_index]

    @property
    def next_leader_id(self):
        return self.member_id_list[self.__next_leader_index()]
        
    @property
    def id(self):
        return self._id