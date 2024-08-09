from pymongo import MongoClient
from pytz import timezone
from datetime import datetime as dt

client = MongoClient("mongodb://codeproject-parser-mongo:27017/codeproject-parser_db")
DB = client['CPService']
# POSTS_COLLECTION = DB['Posts']
POSTS_COLLECTION = DB['test-Posts']


# get current time and convert to TW timezone
def get_curr_time():
    dt_format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = dt.now(timezone('UTC'))
    now_tw = now_utc.astimezone(timezone('Asia/Taipei'))
    return now_tw.strftime(dt_format)


# remove object id
def remove_obj_id(data):
    result = []
    for d in data:
        d.pop("_id")
        result.append(d)
    return result


# query multiple posts in post cache collection by question id
def query_post_by_link(link_list):
    query = {"link": {"$in": link_list}}
    cursor = POSTS_COLLECTION.find(query)
    result = [d for d in cursor]
    return result


# insert multiple posts into post cache collection
def insert_posts(data_list):
    # record insert time
    time = get_curr_time()
    for d in data_list:
        d["saved_time"] = time
    # insert post data
    insert_id = POSTS_COLLECTION.insert_many(data_list)
    return insert_id


# delete multiple posts from cache according to question ids
def delete_posts_by_id(id_list):
    try:
        query = {"question.id": {"$in": id_list}}
        del_result = POSTS_COLLECTION.delete_many(query)
        print(del_result)
    except Exception as e:
        print("Error deleting post cache...\n" + e.__class__.__name__ + ": " + e.args[0])


# auto data maintenance
def cache_maintenance():
    return 0


if __name__ == "__main__":
    print("CodeProject DB Manager v.0")
