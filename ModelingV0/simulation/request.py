from random import randrange
import numpy as np
from scipy.stats import poisson
from scipy.stats import zipf
import matplotlib.pyplot as plt
from numpy import random
import seaborn as sns
from scipy import special
import scipy.stats as stats

class Request:

    @staticmethod
    def generate_sources_random(size_bulk, key_files):
        sources = list()
        for i in range(size_bulk):
            file_rand = randrange(0, len(key_files) - 1)
            sources.append(key_files[file_rand])
        return sources

    @staticmethod
    def generate_sinks_random(size_bulk, key_users):
        sinks = list()
        for i in range(size_bulk):
            user_rand = randrange(0, len(key_users) - 1)
            sinks.append(key_users[user_rand])
        return sinks

    @staticmethod
    def generate_bulk_poisson(avg_size_bulk, num_events):
        return poisson.rvs(mu=avg_size_bulk, size=num_events)

    @staticmethod
    def generate_sources_zip(num_alpha, requests, key_files):
        x = np.arange(1, len(key_files) + 1)
        weights = x ** (-num_alpha)
        weights /= weights.sum()
        bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))
        z = bounded_zipf.rvs(size=requests)

        zipf = list()
        for i in range(len(z)):
            zipf.append(str(z[i]))

        for i in range(len(zipf)):
            filename = key_files[int(zipf[i])-1]
            zipf[i] = str(filename)

        return zipf

