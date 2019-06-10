from aiohttp import web
from threading import Thread, Lock
import time
import json
from .group import Group
from .user import User, UserStatus
import scipy.cluster.hierarchy as sch
import numpy as np
from itertools import compress
import fastcluster as fc
import hdbscan
import traj_dist.distance as tdist # -> url: https://github.com/bguillouet/traj-dist
# TODO : SSL / security logic ?                          

class GroupPowerSaveServer(object):
    def __init__(self):
        self.app = web.Application()
        #TODO register more handlers
        self.app.add_routes([web.post('/register', self.__register_handler)])
        self.app.add_routes([web.put('/user-data', self.__put__data_handler)])
        self.app.add_routes([web.get("/user-data",self.__get_data_handler)])
        self.app.add_routes([web.get("/ping",self.__ping_handler)]) 

        # Worker threads setup
        self.threads = []
        self.threads.append(Thread(target=self.__duty_cycle_tick, args=[5]))
        self.threads.append(Thread(target=self.__group_match_tick, args=[10]))

        self.user_dict_lock = Lock()
        self.user_dict = {}
        self.non_member_id_set = set()
        self.group_dict_lock = Lock()
        self.group_dict = {}

        self.prev_initial_match = []

        for thread in self.threads:
            thread.start()

        web.run_app(self.app)

    def __duty_cycle_tick(self, interval: int):
        leader_update_interval = 30
        while(True):
            # role update
            with self.group_dict_lock:
                for group in self.group_dict.values():
                    if group.is_need_leader_update(leader_update_interval):
                        self.user_dict[group.next_leader_id].reserve_status_change(UserStatus.GROUP_LEADER)

            # TODO duty cycle for group validation / remove non-active user

            time.sleep(interval)

    def __initial_match(self, candidate_list:(np.ndarray, np.generic),min_pts=2, t=10, criterion='maxclust'):
        # TODO group matching for non-grouped user
        # 1 : dbscan algorithm + gps based movement vector alignment -> clear!
        # 2 : acceleration -> let's discuss
        """Performs initial-clustering on cn candidate_list(nT x 2 numpy array) and returns group lists.
        Parameters
        ----------
        candidate_list : array of shape (n_samples, n_of_time_steps, pair of latitude and longitude
        min_pts : minimum members of a group for HDBSCAN-algorithm
        t : scalar
            For criteria 'inconsistent', 'distance' or 'monocrit',
            this is the threshold to apply when forming flat clusters.
            For 'maxclust' or 'maxclust_monocrit' criteria,
            this would be max number of clusters requested.
        criterion : str, optional
        The criterion to use in forming flat clusters. This can
        be any of the following values:

          ``inconsistent`` :
              If a cluster node and all its
              descendants have an inconsistent value less than or equal
              to `t` then all its leaf descendants belong to the
              same flat cluster. When no non-singleton cluster meets
              this criterion, every node is assigned to its own
              cluster. (Default)

          ``distance`` :
              Forms flat clusters so that the original
              observations in each flat cluster have no greater a
              cophenetic distance than `t`.

          ``maxclust`` :
              Finds a minimum threshold ``r`` so that
              the cophenetic distance between any two original
              observations in the same flat cluster is no more than
              ``r`` and no more than `t` flat clusters are formed.

          ``monocrit`` :
              Forms a flat cluster from a cluster node c
              with index i when ``monocrit[j] <= t``.

              For example, to threshold on the maximum mean distance
              as computed in the inconsistency matrix R with a
              threshold of 0.8 do::

                  MR = maxRstat(Z, R, 3)
                  cluster(Z, t=0.8, criterion='monocrit', monocrit=MR)

          ``maxclust_monocrit`` :
              Forms a flat cluster from a
              non-singleton cluster node ``c`` when ``monocrit[i] <=
              r`` for all cluster indices ``i`` below and including
              ``c``. ``r`` is minimized such that no more than ``t``
              flat clusters are formed. monocrit must be
              monotonic. For example, to minimize the threshold t on
              maximum inconsistency values so that no more than 3 flat
              clusters are formed, do::

                  MI = maxinconsts(Z, R)
                  cluster(Z, t=3, criterion='maxclust_monocrit', monocrit=MI)
        Returns
        ----------
        groups : list of shape (n_clusters, n_members)
        
        Examples
        ----------
        >>> candidate_list = np.array([,...,], shape=[5,3,2]) -> labels of candidate_list = [0,1,0,1,0]
        >>> groups = [[0,2,4],[1,3]]
        """
        assert isinstance(candidate_list,(np.ndarray, np.generic))
        num_of_data, num_time_steps, _ = candidate_list.shape
        X = np.array([candidate_list[i,num_time_steps - 1, :] for i in range(num_of_data)])
        rads = np.radians(X)  # [N,2]
        # Clustering with gps-data of 1-time step.
        # 'haversine' do clustering using distance transformed from (lat, long)
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_pts, min_samples=2, metric='haversine')
        labels = clusterer.fit_predict(rads)
        print('Before refinement, labels are ', labels)
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        groups = []
        for ulb in range(n_clusters_):
            groups.append([])
        for i, lb in enumerate(labels):
            if lb == -1:
                continue
            groups[lb].append(i)
        total_n_clusters = n_clusters_
        # Group refinement considering user's trajectory
        for nc in range(n_clusters_):
            group_member_mask = (labels == nc)
            group_members = candidate_list[group_member_mask]
            pdist = tdist.pdist(group_members.transpose([0, 2, 1]),metric="sspd",type_d="spherical")
            Z = fc.linkage(pdist, method="ward")
            sub_labels = sch.fcluster(Z, t, criterion=criterion) - 1
            unique_sub_labels = len(set(sub_labels))
            if unique_sub_labels == 1:
                continue
            for ad in range(unique_sub_labels - 1):
                groups.append([])
            member_indices = list(compress(range(len(group_member_mask)), group_member_mask))
            for sb in range(1, unique_sub_labels):
                sub_group_mask = (sub_labels == sb)
                sub_member_indices = list(compress(range(len(sub_group_mask)), sub_group_mask))
                for m in range(len(sub_member_indices)):
                    # remove from wrong group
                    groups[nc].remove(member_indices[sub_member_indices[m]])
                    # add to refined group
                    groups[total_n_clusters].append(member_indices[sub_member_indices[m]])
                    labels[member_indices[sub_member_indices[m]]] = total_n_clusters
                total_n_clusters += 1
        print('After refinement, labels are ', labels)
        return groups.copy()

    def __group_match(self, candidate_list: list) -> list:
        # Input : list of list of member id
        # output : list of matched group(list of member id) 
        return candidate_list.copy()

    def __group_match_tick(self, interval: int):
        while(True):
            if len(self.prev_initial_match) != 0:
                group_list = self.__group_match(self.prev_initial_match)
                print("Group match result :", group_list)

                group_leader_id_set = set()
                with self.group_dict_lock:
                    for group in self.group_dict.values():
                        group_leader_id_set.add(group.current_leader_id)
                # Create group based on a match result 
                for group_members in group_list:
                    # Find existing groups in a matched group
                    group_leader_indexes = []
                    for id in group_members:
                        if id in group_leader_id_set:
                            group_leader_indexes.append(id)
                    
                    for id in group_leader_indexes:
                        group_members.remove(id)
                    
                    if len(group_leader_indexes) == 0:
                        group = Group(group_members)
                        with self.group_dict_lock:
                            self.group_dict[group.id] = group
                    elif len(group_leader_indexes) == 1:
                        with self.group_dict_lock:
                            group_id = self.user_dict[group_leader_indexes[0]].group_id
                            group = self.group_dict[group_id]
                    # merge groups
                    else:
                        with self.group_dict_lock:
                            main_group_id = self.user_dict[group_leader_indexes[0]].group_id
                            main_group = self.group_dict[main_group_id]
                            print("Group merged main group : ",main_group_id)
                            # Migrate group members to main group
                            for i in range(1, len(group_leader_indexes)):
                                group_id = self.user_dict[group_leader_indexes[i]].group_id
                                group = self.group_dict[group_id]
                                print("Group merged group : ",group_id)
                                for id in group.member_id_list:
                                    self.user_dict[id].reserve_status_change(UserStatus.GROUP_MEMBER, main_group.id)
                                    self.user_dict[id].update_offset(self.user_dict[main_group.current_leader_id])
                                self.group_dict.pop(group_id)
                            
                    for id in group_members:
                        self.non_member_id_set.remove(id)
                        if id == group.current_leader_id:
                            role = UserStatus.GROUP_LEADER
                        else:
                            role = UserStatus.GROUP_MEMBER
                            self.user_dict[id].update_offset(self.user_dict[group.current_leader_id])
                        self.user_dict[id].reserve_status_change(role, group.id)

                self.prev_initial_match.clear()
            
            # Initial match
            if len(self.non_member_id_set) != 0:
                non_member_list = list(self.non_member_id_set)
                non_member_data = []
                for id in non_member_list:
                    if len(self.user_dict[id].gps) >= 3:
                        non_member_data.append([ i[-2:] for i in self.user_dict[id].gps[-3:]])
                
                if len(non_member_data) != 0:
                    # Add existing groups
                    with self.group_dict_lock:
                        for group in self.group_dict.values():
                            leader_id = group.current_leader_id
                            non_member_data.append([ i[-2:] for i in self.user_dict[leader_id].gps[-3:]])
                            non_member_list.append(leader_id)

                    group_indexes = self.__initial_match(np.array(non_member_data))
                    for index_list in group_indexes:
                        if len(index_list) > 1:
                            self.prev_initial_match.append([non_member_list[i] for i in index_list])
                    
                    print("Group initial match result :", self.prev_initial_match)
                    for group_members in self.prev_initial_match:
                        for id in group_members:
                            self.user_dict[id].request_acceleration()
                            print("Requested acceleration to ", id)

            time.sleep(interval)
            
    async def __parse_json(self, request: web.Request, must_contains : list = []):    
        """
        parse json file from request\n
        :param request: http request\n
        :param must_contains: list of keys that json must contain\n
        :return: bool (success), json object or error msg
        """
        try:
            if request.can_read_body:
                json = await request.json()
                not_available_list = []
                for key in must_contains:
                    if key not in json:
                        not_available_list.append(key)
                
                if len(not_available_list) == 0:
                    return True, json
                else:
                    return False, "Doesn't contain : " + "".join(str(x) + " " for x in not_available_list)

        except ValueError:
            return False, "Not able to parse json"

    async def __register_handler(self, request: web.Request) -> web.Response:
        succeess, result = await self.__parse_json(request, ["id"])

        if succeess:
            id = str(result["id"])
            if id in self.user_dict:
                return web.Response(status=422, text="Duplicate id detected : "+str(id))
            with self.user_dict_lock:
                self.user_dict[id] = User(id)
                self.non_member_id_set.add(id)
                print("New Client Registered : ", str(id))
            return web.Response()
        else:
            return web.Response(status=422, text=result)

    async def __put__data_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")

        succeess, result = await self.__parse_json(request, [])
        if succeess:
            user : User = self.user_dict[id]
            user.update_data(result)

            if user.group_id is not None and user.group_id in self.group_dict:
                group : Group = self.group_dict[user.group_id]
                # distribute position to users
                if group.current_leader_id == id:
                    for member_id in group.member_id_list:
                        if member_id != id:
                            self.user_dict[member_id].update_data_from_leader(user)

            return web.Response()
        else:
            return web.Response(status=422, text=result)


    async def __get_data_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")
        
        user = self.user_dict[id]

        user_data = { }

        if len(user.gps) != 0:
            user_data["latitude"] = user.gps[-1][1]
            user_data["longitude"] = user.gps[-1][2]

        return web.json_response(user_data)
    
    async def __ping_handler(self, request: web.Request) -> web.Response:
        id = str(request.rel_url.query['id'])

        # id validation
        if id not in self.user_dict:
            return web.Response(status=422, text="Not valid id")

        user = self.user_dict[id]
        pending_status = user.get_pending_status()

        # update leader the group
        # TODO : missing responde delivery check
        if pending_status is UserStatus.GROUP_LEADER:
            group = self.group_dict[user.group_id]
            if group.current_leader_id != id:
                self.user_dict[group.current_leader_id].reserve_status_change(UserStatus.GROUP_MEMBER)
                group.confirm_leader_update(id)
                # calculate user offsets

                for member in group.member_id_list:
                    if member != id:
                        with self.user_dict_lock:
                            self.user_dict[member].update_offset(user)

        response_data = { "need_acceleration" : user.need_acceleration }

        # let client know about a new role
        if pending_status is not None:
            response_data["status"] = pending_status.value
            response_data["group_id"] = user.group_id

            print("User", id, "has changed to", pending_status)
        
        return web.json_response(response_data)