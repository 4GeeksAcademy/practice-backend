"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
import os
import requests
from flask import request, jsonify


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/places', methods=['POST'])
def get_places_by_cocktail():
    data = request.get_json()

    cocktail = data.get('cocktail')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([cocktail, latitude, longitude]):
        return jsonify({"error": "Missing cocktail or location"}), 400

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    query = "bar"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "type": "bar",
        "key": GOOGLE_API_KEY
    }

    # ✅ Moved below, so variables exist when you print them
    print("GOOGLE API KEY:", GOOGLE_API_KEY)
    print("QUERY:", query)
    print("FULL REQUEST URL:", url)
    print("PARAMS:", params)

    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify({"error": "Failed to fetch data from Google"}), 500

    data = res.json().get("results", [])

    filtered = [
        {
            "name": p["name"],
            "address": p.get("formatted_address"),
            "rating": p.get("rating"),
            "user_ratings_total": p.get("user_ratings_total"),
            "location": p["geometry"]["location"],
            "place_id": p["place_id"],
            "photo_reference": p["photos"][0]["photo_reference"] if p.get("photos") else None
        }
        for p in data if p.get("business_status") == "OPERATIONAL"
    ]

    return jsonify(filtered), 200

    


