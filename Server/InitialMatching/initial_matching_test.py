import numpy as np
from sklearn.preprocessing import StandardScaler
import scipy.cluster.hierarchy as sch
from IO_event import IndexTracker
import matplotlib.pyplot as plt
from itertools import compress
import fastcluster as fc
import cv2 as cv
import hdbscan
import traj_dist.distance as tdist


def __initial_match(candidate_list: (np.ndarray, np.generic), min_pts=2, t=50, criterion='distance'):
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
    assert isinstance(candidate_list, (np.ndarray, np.generic))
    num_of_data, num_time_steps, _ = candidate_list.shape
    X = np.array([candidate_list[i, num_time_steps - 1, :] for i in range(num_of_data)])
    rads = np.radians(X)  # [N,2]
    # Clustering with gps-data of 1-time step.
    # 'haversine' do clustering using distance transformed from (lat, long)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_pts, min_samples=2, metric='haversine')
    labels = clusterer.fit_predict(rads)
    print('Before trajectory clustering, labels are ', labels)
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
        pdist = tdist.pdist(group_members.transpose([0, 2, 1]), metric="sspd",type_d="spherical")
        Z = fc.linkage(pdist, method="ward")
        sub_labels = sch.fcluster(Z, t, criterion=criterion) - 1
        unique_sub_labels = len(set(sub_labels))
        if unique_sub_labels == 1:
            continue
        for ad in range(unique_sub_labels - 1):
            groups.append([])
        member_indices = list(compress(range(len(group_member_mask)), group_member_mask))
        for sb in range(unique_sub_labels):
            sub_group_mask = (sub_labels == sb)
            sub_member_indices = list(compress(range(len(sub_group_mask)), sub_group_mask))
            #Noise case
            if len(sub_member_indices) == 1:
                groups[nc].remove(member_indices[sub_member_indices[0]])
                labels[member_indices[sub_member_indices[0]]] = -1
                continue
            for m in range(len(sub_member_indices)):
                # remove from wrong group
                groups[nc].remove(member_indices[sub_member_indices[m]])
                # add to refined group
                groups[total_n_clusters].append(member_indices[sub_member_indices[m]])
                labels[member_indices[sub_member_indices[m]]] = total_n_clusters
            total_n_clusters += 1
    print('After trajectory clustering, labels are ', labels)
    return groups.copy()
if __name__=="__main__":
    npy_path = 'D:/python/clustering-mobilecomputing/dbscan/DBSCAN-test/snu-amc-s19-team7/Server/InitialMatching/traj_streams.npy'
    gen_mode = False
    num_of_data = 5
    num_time_steps = 3
    # Data generation
    if gen_mode == True:#-> data_generation mode
        map_path = 'D:/python/clustering-mobilecomputing/dbscan/snu_map.png'
        fig, ax = plt.subplots(1, 1)
        map_image = cv.imread(map_path,cv.IMREAD_COLOR)
        ax.set_title('Draw the trajectories in map !')
        tracker = IndexTracker(ax, plt, map_image)
        fig.canvas.mpl_connect('button_press_event', tracker.click)
        fig.canvas.mpl_connect('key_press_event', tracker.key_board)
        plt.show()
        print('Num of people :',tracker.num + 1)
        print('Time steps:',len(tracker.data[0]))
        num_of_data = tracker.num+1
        data_track = tracker.data[:num_of_data]
        num_time_steps = len(data_track[0])
        streamlines = np.vstack(data_track)
        # X = [data_track[i][num_time_steps-1] for i in range(num_of_data)]
        streamlines = StandardScaler().fit_transform(streamlines)#평균0,분산1이 되도록 데이터 전처리.
        np.save(npy_path, streamlines)
    # streamlines = np.load(npy_path)
    streamlines = np.array([[[37.459789,126.956361],[37.460028,126.956567],[37.460125,126.956770]],\
                   [[37.459587,126.957122],[37.459902,126.957090],[37.460128,126.956932]],
                   [[37.459839,126.957106],[37.459990,126.957058],[37.460166,126.956932]],
                   [[37.459638,126.956662],[37.459877,126.956773],[37.460103,126.956827]],
                   [[37.461008,126.956382],[37.460892,126.956498],[37.460587,126.956702]]])
    streamlines = streamlines.reshape([num_of_data,num_time_steps,2])
    __initial_match(streamlines)