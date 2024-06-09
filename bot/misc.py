from redis.asyncio import Redis

# dev
# redis = Redis(host="localhost", port=6379, db=0)

# prod
redis = Redis(host="localhost", port=6379, db=0)
