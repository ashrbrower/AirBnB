import httpx
from mcp.server import MCPServer

API = "http://127.0.0.1:8000"

mcp = MCPServer("Airbnb-Movie Server")


def call_flask(base_url: str, endpoint: str, params: dict):
    """Call an existing Flask REST API and return JSON."""

    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            base_url + endpoint,
            params=params
        )

        response.raise_for_status()
        return response.json()


# ============================================================
# MOVIES
# ============================================================

@mcp.tool()
def search_movies(
    title: str = "",
    genre: str = "",
    votes: int = 0,
    rating: int = 0,
    release_year: int = 0,
    rating_higher: str = ""
) -> list:
    """
    Search movies by title, genre, rating, votes, and release year. Rating higher = true for scores including rating and up, false for including rating and down.

    Examples:
    - Find action movies
    - Movies rated higher than 8
    - Movies released in 2020
    """

    params = {}

    if title:
        params["title"] = title

    if genre:
        params["genre"] = genre

    if votes:
        params["votes"] = votes

    if rating:
        params["rating"] = rating

    if release_year:
        params["release_year"] = release_year

    if rating_higher:
        params["rating_higher"] = rating_higher

    return call_flask(
        API,
        "/movies",
        params
    )


# ============================================================
# AIRBNB DESTINATIONS
# ============================================================

@mcp.tool()
def get_top_destinations(
    country: str = "",
    city: str = "",
    limit: int = 10
) -> list:
    """
    Return the most popular Airbnb destinations.

    Examples:
    - What are the top Airbnb destinations?
    - What are the top destinations in Turkey?
    - Show the most popular places in Brazil.
    """

    return call_flask(
        API,
        "/markets/top-destinations",
        {
            "country": country,
            "city": city,
            "limit": limit
        }
    )


# ============================================================
# AMENITIES
# ============================================================

@mcp.tool()
def get_trending_amenities(
    limit: int = 20
) -> list:
    """
    Return the most popular Airbnb amenities.

    Examples:
    - What amenities are most common?
    - What do most Airbnb properties offer?
    """

    return call_flask(
        API,
        "/amenities/trending",
        {
            "limit": limit
        }
    )


# ============================================================
# PRICE ANALYTICS
# ============================================================

@mcp.tool()
def get_average_prices(
    country: str = "",
    city: str = ""
) -> list:
    """
    Return average Airbnb prices grouped by market.

    Examples:
    - What are average Airbnb prices in Brazil?
    - Compare prices across cities.
    - What is the average Airbnb price in Rio De Janeiro?
    """

    return call_flask(
        API,
        "/markets/average-prices",
        {
            "country": country,
            "city": city
        }
    )


# ============================================================
# HOST ANALYTICS
# ============================================================

@mcp.tool()
def get_top_hosts(
    country: str = "",
    city: str = "",
    limit: int = 10
) -> list:
    """
    Return Airbnb hosts with the most listings.

    Examples:
    - Who are the top Airbnb hosts?
    - Who manages the most properties in Brazil?
    - Show top hosts in Istanbul.
    """

    return call_flask(
        API,
        "/hosts/top-hosts",
        {
            "country": country,
            "city": city,
            "limit": limit
        }
    )


# ============================================================
# GEO SEARCH
# ============================================================

@mcp.tool()
def find_nearby_listings(
    latitude: float,
    longitude: float,
    radius: int = 5000
) -> list:
    """
    Find Airbnb listings near a location.

    Radius is specified in meters.

    Examples:
    - Find Airbnbs near Istanbul.
    - Show listings within 10km of Rio De Janeiro.
    - What Airbnb properties are nearby?
    """

    return call_flask(
        API,
        "/listings/nearby",
        {
            "lat": latitude,
            "lng": longitude,
            "radius": radius
        }
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=5000
    )