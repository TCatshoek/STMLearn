import pickle
# import numpy as np
# from util.editdistance import lcsdistance
# from scipy.cluster.hierarchy import linkage, dendrogram
# from scipy.spatial.distance import squareform
# import matplotlib.pyplot as plt
# from scipy.cluster.hierarchy import fcluster
# import random

# Borg pattern for EZ singletons https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html

class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

class CounterexampleTracker(Borg):
    def __init__(self):
        Borg.__init__(self)

        if 'storage' not in self.__dict__.keys():
            self.storage = []

    def add(self, counterexample):
        self.storage.append(counterexample)

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.storage, file)

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.storage = pickle.load(file)
    #
    # def distance_matrix(self, penalty=0):
    #     n = len(self.storage)
    #     m = np.zeros((n, n))
    #
    #     for row in range(n):
    #         for col in range(n):
    #             m[row, col] = lcsdistance(self.storage[row], self.storage[col], penalty=penalty)
    #
    #     return m
    #
    # def get_clusters(self,
    #                  penalty=0,
    #                  t=1,
    #                  linkage_method='single'):
    #
    #     if len(self.storage) < 2:
    #         return self.storage
    #
    #     dists = self.distance_matrix(penalty)
    #     linkages = linkage(squareform(dists), method=linkage_method)
    #     cluster_assignments = fcluster(linkages, t=t)
    #     cluster_labels = np.unique(cluster_assignments)
    #
    #     counterexamples = np.array(self.storage)
    #     clusters = []
    #     for label in cluster_labels:
    #         clusters.append(counterexamples[cluster_assignments == label])
    #
    #     return clusters