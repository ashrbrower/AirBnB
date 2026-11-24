import redis
import yaml
from pymongo import MongoClient


def load_config():
    """Load configuration from the YAML file.

    Returns:
        dict: Configuration data.
    """
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()

def get_redis_connection():
    """Create a Redis connection using the configuration.

    Returns:
        Redis: Redis connection object.
    """
    return redis.Redis(
        host=config["redis"]["host"],
        port=config["redis"]["port"],
        db=0,
        decode_responses=True,
        username=config["redis"]["user"],
        password=config["redis"]["password"],
    )

def get_mongo_connection():
    """Create a MongoDB connection using the configuration.
    
        Returns:
            Mongo collection object.
        """
    uri = config["mongodb"]["uri"]
    uri = uri.replace("<db_username>", config["mongodb"]["user"])
    uri = uri.replace("<db_password>", config["mongodb"]["password"])
    db = MongoClient(uri)["sample_airbnb"]
    
    return db["listingsAndReviews"]