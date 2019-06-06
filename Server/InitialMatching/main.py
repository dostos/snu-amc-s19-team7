# print(__doc__)
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
# from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from IO_event import IndexTracker
import cv2 as cv
import matplotlib.pyplot as plt
"""""""""""""  Parameters  """""""""""""
path = 'D:/python/clustering-mobilecomputing/dbscan/snu_map.png'
labels_true = [0,0,1,2,0,1,1,2,0,2]
num_of_data = len(labels_true)
max_time_steps = 5
ARI = 0
eps = 0.05
min_pts = 2
""""""""""""""""""""""""""""""""""""""
fig, ax = plt.subplots(1, 1)
map_image = cv.imread(path,cv.IMREAD_COLOR)
ax.set_title('labels: {0}'.format(labels_true))
tracker = IndexTracker(ax, plt, map_image, num_of_data, max_time_steps)
fig.canvas.mpl_connect('button_press_event', tracker.click)
fig.canvas.mpl_connect('key_press_event', tracker.key_board)
plt.show()
print('Num of people :',tracker.num + 1)
print('Time steps:',len(tracker.data[0]))
print('Dataset:',tracker.data)
# num_data = tracker.num
data_track = tracker.data[:num_of_data]
num_time_steps = len(data_track[0])
X = [data_track[i][num_time_steps-1] for i in range(num_of_data)]
# Generate sample data
# centers = [[1, 1], [-1, -1], [1, -1]]
# X, labels_true = make_blobs(n_samples=750, centers=5, cluster_std=0.4,
#                             random_state=0)
X = StandardScaler().fit_transform(X)#평균0,분산1이 되도록 데이터 전처리.
# Compute DBSCAN
while ARI <= 0.99:
    db = DBSCAN(eps=eps, min_samples=min_pts).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    ARI = metrics.adjusted_rand_score(labels_true, labels)
    eps += 0.05
print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
print("Adjusted Rand Index: %0.3f"
      % metrics.adjusted_rand_score(labels_true, labels))
print("Adjusted Mutual Information: %0.3f"
      % metrics.adjusted_mutual_info_score(labels_true, labels,
                                           average_method='arithmetic'))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))

# #############################################################################
# Plot result
import matplotlib.pyplot as plt

# Black removed and is used for noise instead.
unique_labels = set(labels)#순서대로 정렬
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]
    class_member_mask = (labels == k)
    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)
    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)
plt.title('Estimated number of clusters: %d, Epsilon: %f ,Min_pts: %d'%(n_clusters_,eps,min_pts))
plt.show()