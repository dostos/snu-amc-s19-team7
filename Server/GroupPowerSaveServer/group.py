
class Group(object):
    # static count for group id
    unique_id_count = 0

    @staticmethod
    def get_unique_id():
        id = Group.unique_id_count
        Group.unique_id_count +=1
        return id

    def __init__(self, id, member_id_list : list  = []):
        self._id = id
        self.member_id_list = member_id_list
    
    @property
    def id(self):
        return self._id