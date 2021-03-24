from random import randrange
import numpy as np


class Request:

    @staticmethod
    def generate_request(num_requests, key_files, key_users, sources, sinks):
        for i in range(num_requests):
            file_rand = randrange(0, len(key_files) - 1)
            user_rand = randrange(0, len(key_users) - 1)
            sources.append(key_files[file_rand])
            sinks.append(key_users[user_rand])
        sources = np.array(sources)
        sinks = np.array(sinks)