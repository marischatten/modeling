from random import randrange
import numpy as np
from scipy.stats import poisson
from scipy.stats import zipf
import matplotlib.pyplot as plt
from numpy import random
import seaborn as sns
from scipy import special

class Request:

    @staticmethod
    def generate_sources_random(size_bulk, key_files):
        sources = list()
        for i in range(size_bulk):
            file_rand = randrange(0, len(key_files) - 1)
            sources.append(key_files[file_rand])
        return sources

    @staticmethod
    def generate_sources_zipf(num_alpha,size_bulks, num_events,key_files):
        sources = list()
        all_req = 0
        for event in range(num_events):
            all_req += size_bulks[event]

        file_zipf = zipf.rvs(num_alpha, all_req)

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
    def generate_bulk_zip(num_alpha, requests,num_events,size_bulks):
        #x = random.zipf(a=2.7,size=10)
        #plt.xlim(10)
        #print(x)
        #sns.distplot(x)
        #plt.legend()
        #plt.show()
        #all_req = 0
        #for event in range(num_events):
         #   all_req += size_bulks[event]

        a = 2.  # parameter
        s = np.random.zipf(a, 1000)
        print(s)
        count, bins, ignored = plt.hist(s[s < 10], 10, density=True)
        x = np.arange(1., 10.)
        y = x ** (-a) / special.zetac(a)
        #plt.yscale('log')
        plt.title('Zipf')
        plt.xlabel('rank')
        plt.ylabel('frequency')

        plt.plot(x, y / max(y), linewidth=2, color='r')
        plt.show()
