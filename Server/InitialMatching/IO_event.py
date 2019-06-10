from __future__ import print_function
import numpy as np
import matplotlib.cm as cm

N_color = 10
class IndexTracker(object):
    def __init__(self, ax,plt, X):
        self.ax = ax
        self.plt = plt
        # ax.set_title('use scroll wheel to navigate images')
        self.X = X
        self.data=[[] for _ in range(100)]
        x = np.arange(N_color)
        ys = [i + x + (i * x) ** 2 for i in range(N_color)]
        self.colors = cm.rainbow(np.linspace(0, 1, len(ys)))
        self.im = ax.imshow(self.X)
        self.num = 0
        self.steps = 0
    def key_board(self, event):
        if event.key == 'a' or event.key == 'A':
            self.num += 1
            self.steps = 0
            print('Change label to {0}'.format(self.num))
        if event.key == 'e' or event.key == 'E':
            print('Finish data generation !')
            self.plt.close('all')
    def click(self,event):
        x_p = event.xdata
        y_p = event.ydata
        self.data[self.num].append([x_p,y_p])
        self.steps += 1
        self.X[int(y_p),int(x_p), 0] = 255
        self.X[int(y_p), int(x_p), 1] = 0
        self.X[int(y_p), int(x_p), 2] = 0
        self.plt.scatter(x_p, y_p,s=20,marker='o',color=self.colors[self.num % N_color])
        print('you pressed ({0}, {1}) '.format(x_p, y_p))
        # if self.steps == self.max_time_steps:
        #     self.num += 1
        #     self.steps = 0
        #     print('Change label to {0}'.format(self.num))
        self.plt.show()
