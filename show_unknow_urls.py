import redis
import os
import sys
import traceback

gUNKNOW_URL_KEY_NAME = 'guide:protect:unknow_urls'

def get_unknow_redis_db(host='127.0.0.1', port=6379,db=1):

    try:
        redis_obj = redis.Redis(host=host, port=port, db=db)
        return redis_obj
    except Exception, e:
        print (str(e))
        print(traceback.format_exc())

redis_obj = get_unknow_redis_db()
print 'range:'
print redis_obj.lrange(gUNKNOW_URL_KEY_NAME, 0, 30)
print 'len:', redis_obj.llen(gUNKNOW_URL_KEY_NAME)
