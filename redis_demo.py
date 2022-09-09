import redis # https://github.com/redis/redis-py#installation
import os


def createClient():
    print('Connecting to client')
    hostname = os.environ['HOSTNAME'] 
    password = os.environ['PASSWORD'] 
    client = redis.Redis(
        host=hostname, # 11-11-11-11.dbaas.intel.com
        port=6379, # 6379 is default non-TLS port
        password=password, # Password for Default user found in dbaas.intel.com
        charset='utf-8', # Normalize the DB entries
        decode_responses=True # Normalized the DB entries
    )
    return client

def main():
    # Create Redis instance
    redis_instance = createClient()    
    # Test setting and getting values
    redis_instance.set('PING', 'PONG')
    print('Pinging Redis instance: ')
    print(redis_instance.get('PING'))
    exit(0)
    
if __name__ == "__main__":
    main()