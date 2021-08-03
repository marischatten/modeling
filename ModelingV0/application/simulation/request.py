import sys
from random import randrange
from scipy.stats import poisson
import scipy.stats as stats
from utils.utils import *
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class Request:

    @staticmethod
    def create_requests(avg_qtd_bulk, num_events, num_alpha, key_index_file, key_index_ue,
                        num_files,plot_distribution=False, fixed=False):
        requests = list()
        if fixed:
            bulks = np.array([avg_qtd_bulk for i in range(num_events)])
        else:
            bulks = Request.__generate_bulk_poisson(avg_qtd_bulk, num_events)
            bulks = Request.__remove_bulk_empty(bulks.copy())

        zipf = Request.__generate_sources_zip(num_alpha, sum(bulks), key_index_file)
        count = 0
        for r in range(sum(bulks)):
            s = zipf[r]
            t = Request.__generate_sink_random(key_index_ue)
            pair = (s, t)
            if (len(requests) != 0):
                while Request.__is_replicated(requests, pair):
                    count += 1
                    if count == len(key_index_ue):
                        print(REVERSE,
                              "Impossible to generate this amount of unreplicated requests for this instance.\n Please, decrease the number of requests or change for larger instance.",
                              RESET)
                        sys.exit()
                    print("Removed Replicated Request.")
                    t = Request.__generate_sink_random(key_index_ue)
                    pair = (s, t)
                count = 0
                requests.append(pair)
            else:
                pair = (s, t)
                requests.append(pair)

        if plot_distribution:
            Request.__plot_poisson(bulks)
            Request.__plot_zipf(zipf, num_files)

        return (requests, bulks)

    @classmethod
    def __generate_sinks_random(self, size_bulk, key_users):
        sinks = list()
        for i in range(size_bulk):
            user_rand = randrange(0, len(key_users) - 1)
            sinks.append(key_users[user_rand])
        return sinks

    @classmethod
    def __generate_sink_random(self, key_users):
        user_rand = randrange(0, len(key_users) - 1)
        return key_users[user_rand]

    @classmethod
    def __generate_bulk_poisson(self, avg_size_bulk, num_events):
        return poisson.rvs(mu=avg_size_bulk, size=num_events)

    @classmethod
    def __generate_sources_zip(self, num_alpha, requests, key_files):
        # 1/n**a
        x = np.arange(1, len(key_files) + 1)
        weights = x ** (-num_alpha)
        weights /= weights.sum()
        bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))
        z = bounded_zipf.rvs(size=requests)

        zipf = list()
        for i in range(len(z)):
            zipf.append(str(z[i]))

        for i in range(len(zipf)):
            filename = key_files[int(zipf[i]) - 1]
            zipf[i] = str(filename)

        return zipf

    @classmethod
    def __is_replicated(self, requests, pair):
        if pair in requests:
            return True
        return False

    @classmethod
    def __remove_bulk_empty(self, bulks):
        for b in range(len(bulks)):
            if bulks[b] == 0:
                bulks[b] = 1
        return bulks

    @classmethod
    def __plot_poisson(self, distribution):
        sns.displot(distribution)
        plt.xlim([0, 25])
        plt.xlabel('k')
        plt.ylabel('P(X=k)')
        plt.show()

    @classmethod
    def __plot_zipf(self, distribution, num_files):
        plt.hist(distribution, bins=np.arange(1, num_files + 1), density=True)
        # plt.hist(distribution[distribution < 10], 10, density=True)
        # x = np.arange(1., 10.)
        # y = x ** (-alpha) / special.zetac(alpha)
        # plt.yscale('log')
        plt.title('Zipf')
        plt.xlabel('rank')
        plt.ylabel('frequency')
        # plt.plot(x, y / max(y), linewidth=2, color='r')
        plt.show()
