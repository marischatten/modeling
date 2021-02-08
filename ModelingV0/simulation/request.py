from random import randrange


class Request:


    @staticmethod
    def generate_request( num_requests, num_ue_bottom, num_ue_top, num_files):
        requests = dict()
        for i in range(num_requests):
            user_node = randrange(num_ue_bottom, num_ue_top)
            node_req = randrange(0,num_ue_bottom-1)
            file = randrange(0, num_files)
            requests.update({i: (user_node, node_req,file)})
        return requests
