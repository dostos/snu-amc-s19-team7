from threading import Lock

class Group(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def get_unique_id():
        id = Group.unique_id_count
        Group.unique_id_count +=1
        return id

    def __init__(self, id, member_id_list : list = []):
        self._id = id
        self.member_id_list = member_id_list
        self.lock = Lock()
        self.leader_iterator = None

    def add_member(self, id):
        with self.lock:
            self.member_id_list.add(id)
    
    def get_next_leader(self, id):
        pass
        #with self.lock:
            #if self.leader_iterator is None:
            #    self.leader_iterator = self.member_id_list.

    @property
    def id(self):
        return self._id