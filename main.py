from db_config import get_redis_connection, get_mongo_connection
from redis.commands.search.query import Query
from flask import Flask, jsonify, request
import json

from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Flask App using Mongo/Redis",
)


movie_model = api.model(
    "Movie",
    {
        "title": fields.String(description="Movie Title", required=False),
        "genre": fields.String(description="Movie Genre", required=False),
        "votes": fields.Integer(description="Number of votes", required=False),
        "rating": fields.Integer(description="Movie Rating", required=False),
        "release_year": fields.Integer(description="Movie Release Year", required=False)
    },
)

@api.route("/movies", methods=["GET"])
class movie(Resource):
    @api.doc(model=[movie_model])
    def get(self):
        title = request.args.get("title")
        genre = request.args.get("genre")
        votes = request.args.get("votes")
        rating = request.args.get("rating")
        release_year = request.args.get("release_year")
        rating_higher = request.args.get("rating_higher") # True = rating value and higher, False = rating value and lower, None = exact rating value

        filters = []
        if title:
            filters.append(f"@title:{title}")

        if genre:
            filters.append(f"@genre:{{{genre}}}")

        if votes:
            filters.append(f"@votes:[{votes} +inf]")
        if rating:
            if rating_higher is None:
                filters.append(f"@rating:[{rating} {rating}]")
            elif rating_higher.lower() == "true":
                filters.append(f"@rating:[{rating} +inf]")
            elif rating_higher.lower() == "false":
                filters.append(f"@rating:[-inf {rating}]")

        if release_year:
            filters.append(f"@release_year:[{release_year} {release_year}]")

        # Join all active filters with spaces (AND), or default to "*" if none provided
        search_str = " ".join(filters) if filters else "*"

        redis_conn = get_redis_connection()
        print(title)

        query = Query(search_str).paging(0, 1000)
        results = redis_conn.ft("idx:movie").search(query)

        movies = [doc.__dict__ for doc in results.docs]
        return jsonify(movies)

@api.route("/markets/top-destinations", methods=["GET"])
class TopDestinations(Resource):

    def get(self):
        collection = get_mongo_connection()
        limit = int(request.args.get("limit", 10))
        country = request.args.get("country")
        city = request.args.get("city")

        print (country, city)
        match_filter = {}
        pipeline = []
        if country:
            match_filter["address.country"] = country

        if city:
            match_filter["address.market"] = city

        if match_filter:
            pipeline.append({
                "$match": match_filter
            })

        pipeline.extend([
            {
                "$group": {
                    "_id": "$address.market",
                    "country": {
                        "$first": "$address.country"
                    },
                    "listingCount": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "listingCount": -1
                }
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "market": "$_id",
                    "country": 1,
                    "listingCount": 1
                }
            }
        ])

        results = list(collection.aggregate(pipeline))

        return jsonify(results)


@api.route("/amenities/trending", methods=["GET"])
class TrendingAmenities(Resource):

    def get(self):
        collection = get_mongo_connection()

        limit = int(request.args.get("limit", 20))

        pipeline = [
            {
                "$unwind": "$amenities"
            },
            {
                "$group": {
                    "_id": "$amenities",
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "amenity": "$_id",
                    "count": 1
                }
            }
        ]

        results = list(collection.aggregate(pipeline))

        return jsonify(results)


@api.route("/markets/average-prices", methods=["GET"])
class AveragePrices(Resource):

    def get(self):
        collection = get_mongo_connection()
        country = request.args.get("country")
        city = request.args.get("city")
        pipeline = []

        if country:
            pipeline.append({
                "$match": {
                    "address.country": country
                }
            })
        if city:
            pipeline.append({
                "$match": {
                    "address.market": city
                }
            })

        pipeline.extend([
            {
                "$group": {
                    "_id": "$address.market",
                    "country": {
                        "$first": "$address.country"
                    },
                    "averagePrice": {
                        "$avg": {
                            "$toDouble": "$price"
                        }
                    },
                    "listingCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "averagePrice": -1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "market": "$_id",
                    "country": 1,
                    "averagePrice": {
                        "$round": [
                            "$averagePrice",
                            2
                        ]
                    },
                    "listingCount": 1
                }
            }
        ])

        results = list(collection.aggregate(pipeline))

        return jsonify(results)


@api.route("/hosts/top-hosts", methods=["GET"])
class TopHosts(Resource):

    def get(self):
        collection = get_mongo_connection()
        limit = int(request.args.get("limit", 10))
        country = request.args.get("country")
        city = request.args.get("city")

        pipeline = []

        match_filter = {}

        if country:
            match_filter["address.country"] = country

        if city:
            match_filter["address.market"] = city

        if match_filter:
            pipeline.append({
                "$match": match_filter
            })

        pipeline.extend([
            {
                "$group": {
                    "_id": "$host.host_id",
                    "hostName": {
                        "$first": "$host.host_name"
                    },
                    "listingCount": {
                        "$sum": 1
                    },
                    "superhost": {
                        "$first": "$host.host_is_superhost"
                    },
                    "country": {
                        "$first": "$address.country"
                    },
                    "market": {
                        "$first": "$address.market"
                    }
                }
            },
            {
                "$sort": {
                    "listingCount": -1
                }
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "hostId": "$_id",
                    "hostName": 1,
                    "listingCount": 1,
                    "superhost": 1,
                    "country": 1,
                    "market": 1
                }
            }
        ])

        results = list(collection.aggregate(pipeline))

        return jsonify(results)


@api.route("/listings/nearby", methods=["GET"])
class NearbyListings(Resource):

    def get(self):
        collection = get_mongo_connection()
        latitude = float(request.args.get("lat"))
        longitude = float(request.args.get("lng"))
        radius = int(request.args.get("radius", 5000))

        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [
                            longitude,
                            latitude
                        ]
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "maxDistance": radius
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "property_type": 1,
                    "room_type": 1,
                    "street": "$address.street",
                    "price": {
                        "$toDouble": "$price"
                    },
                    "distanceKm": {
                        "$round": [
                            {
                                "$divide": [
                                    "$distance",
                                    1000
                                ]
                            },
                            2
                        ]
                    }
                }
            },
            {
                "$limit": 20
            }
        ]

        results = list(collection.aggregate(pipeline))

        return jsonify(results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)