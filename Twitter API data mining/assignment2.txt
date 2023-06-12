# Cook book functions.
# All code in this file is taken from Chapter 9 - Twitter Cookbook.
# Import required packages.
import twitter
from functools import partial
from sys import maxsize as maxint
import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import networkx as nx
import json
import matplotlib.pyplot as plt


API_key = "5hxPiteIhuzXBDk35BsDzdT8U"


API_key_secret = "Vqt1kSm01UdgJ4hxPfH12OW78Fs2uyOjXrMA6dIXHbFyqIT9md"

Access_Token="1182358903436263427-jszOyBJxRhnZFPxksL7rkECekD2NLF"
Access_Token_Secret="UMjXUxIknhtGKv9hGQN7sHNNvh41qlawvBJO5SsDHpmbC"

# Taken from example 1 of Chapter 9 - Twitter Cookbook
def oauth_login(): #authentication
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://developer.twitter.com/en/docs/basics/authentication/overview/oauth
    # for more information on Twitter's OAuth implementation.

    CONSUMER_KEY = "5hxPiteIhuzXBDk35BsDzdT8U"
    CONSUMER_SECRET = "Vqt1kSm01UdgJ4hxPfH12OW78Fs2uyOjXrMA6dIXHbFyqIT9md"
    OAUTH_TOKEN = "1182358903436263427-jszOyBJxRhnZFPxksL7rkECekD2NLF"
    OAUTH_TOKEN_SECRET = "UMjXUxIknhtGKv9hGQN7sHNNvh41qlawvBJO5SsDHpmbC"

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


# Taken from chapter 19 of twitter cookbook
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e

        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes

        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429:
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60 * 15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e  # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds' \
                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise



# Taken from Chapter 9 - twitter cookbook
def get_user_profile(twitter_api, screen_names=None, user_ids=None):
    # Must have either screen_name or user_id (logical xor)
    assert (screen_names != None) != (user_ids != None), \
        "Must have screen_names or user_ids, but not both"

    items_to_info = {}

    items = screen_names or user_ids

    while len(items) > 0:

        # Process 100 items at a time per the API specifications for /users/lookup.
        # See http://bit.ly/2Gcjfzr for details.

        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup,
                                            screen_name=items_str)
        else:  # user_ids
            response = make_twitter_request(twitter_api.users.lookup,
                                            user_id=items_str)

        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info
            else:  # user_ids
                items_to_info[user_info['id']] = user_info

    return items_to_info


#The key function for getting the followers count of a user
def followers_count(x):#x is a tuple of the form (<user id>, <user's profile dict>)
    return x[1]['followers_count']

def get_reciprocal_friends_ids(twitter_api,ids, screen_name=None, user_id=None, friends_limit=10000):
    assert(screen_name and not user_id or user_id and not screen_name)# assert screen name xor user id
    if screen_name:
        response_friends = make_twitter_request(twitter_api.friends.ids,screen_name=screen_name, count=friends_limit)
        response_followers = make_twitter_request(twitter_api.followers.ids,screen_name=screen_name, count=friends_limit)

    else:
        response_friends = make_twitter_request(twitter_api.friends.ids,user_id=user_id, count=friends_limit)
        response_followers = make_twitter_request(twitter_api.followers.ids,user_id=user_id, count=friends_limit)


    friends = response_friends["ids"]
    followers = response_followers["ids"]
    reciprocal_friends = list(set(friends).intersection(set(followers)))# from the textbook, then cast to list so it's iterable
    while(len(reciprocal_friends)<1 and (len(friends) == friends_limit or len(followers)==friends_limit) and friends_limit<20000):#had issue with getting disjoint sets for friends and followers
        friends_limit*=2
        print('doubling')
        if screen_name:
            if len(friends) == friends_limit/2:
                response_friends = make_twitter_request(twitter_api.friends.ids, screen_name=screen_name,
                                                        count=friends_limit)
            if len(followers) == friends_limit/2:
                response_followers = make_twitter_request(twitter_api.followers.ids, screen_name=screen_name,
                                                          count=friends_limit)

        else:
            if len(friends) == friends_limit / 2:
                response_friends = make_twitter_request(twitter_api.friends.ids, user_id=user_id, count=friends_limit)
            if len(followers) == friends_limit / 2:
                response_followers = make_twitter_request(twitter_api.followers.ids, user_id=user_id, count=friends_limit)

        friends = response_friends["ids"]
        followers = response_followers["ids"]
        reciprocal_friends = list(set(friends).intersection(set(followers)))  # from the textbook, then cast to list so it's iterable

    five_most_popular = []
    profiles = get_user_profile(twitter_api=twitter_api,user_ids=reciprocal_friends)#textbook function
    profiles = [(key,value) for key, value  in profiles.items()]#cast dict to list of key value pairs to make it iterable
    """    for rf in reciprocal_friends:
        curr = get_user_profile(twitter_api=twitter_api,user_ids=[rf])
        break"""

    #print(friends)
    try:#in case we get very few reciprocal friends, just get these nodes
        for i in range(5):#5 most popular friends
            biggest = max(profiles,key=followers_count)#find the max with key as function above
            if biggest not in ids:#make sure not to double count
                five_most_popular.append(biggest)#append max to list
            else:
                i-=1
            profiles.remove(biggest)#remove from list
    except:
        pass
    #print(five_most_popular)
    return [x[0] for x in five_most_popular]#only return the list of IDs

def crawler(twitter_api,starting_point):
    try:#I keep running out of rate limit, so I put this in a try block so I can at least get an output graph
        G = nx.Graph()#initialize graph
        ids = [starting_point]
        response = get_reciprocal_friends_ids(twitter_api,ids,screen_name=starting_point)#modified textbook function to get reciprocal friends ids

        G.add_node(starting_point)#add starting node
        G.add_nodes_from(response)#add response nodes
        G.add_edges_from([(starting_point, x) for x in response])#create edges
        next_queue = response
        ids += next_queue
        depth = 1
        max_depth = 4
        while len(ids)<100:# make sure we get at least 100 nodes, BFS... Don't want this program to take forever, so I'm ignoring max depth.
            depth += 1
            (queue, next_queue) = (next_queue, [])
            for id in queue:
                response = get_reciprocal_friends_ids(twitter_api,ids, user_id=id, friends_limit=5000)#modified textbook function
                G.add_nodes_from(response)
                G.add_edges_from([(id,x) for x in response])
                next_queue += response
            ids += next_queue
    except:
        return G
    return G


starting_point_screen_name = "JoeShmoeNFT"

twitter_api = oauth_login()
G = crawler(twitter_api=twitter_api,starting_point=starting_point_screen_name)
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())
print("The diameter is:",nx.diameter(G))#NetworkX functions..
print("The average distance is:",nx.average_shortest_path_length(G))
nx.draw(G)
plt.savefig("mygraph.png")
plt.show()








