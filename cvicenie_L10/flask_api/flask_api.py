#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask REST API pre senzorové dáta
"""

from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime
import logging

# Nastavenie logovania pre jednoduchšie debugovanie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurácia databázy - jednoduché a prehľadné
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
DB_NAME = os.getenv("DB_NAME", "robot_dreams_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sensors")

# Vytvorenie Flask aplikácie
app = Flask(__name__)

# Jednoduché pripojenie k MongoDB
try:
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Test pripojenia
    client.admin.command("ping")
    logger.info(f"Pripojené k MongoDB: {MONGO_HOST}:{MONGO_PORT}")
except Exception as e:
    logger.error(f"Chyba pripojenia k MongoDB: {e}")
    exit(1)

# =============================================================================
# API ENDPOINTS - Jednoduché senzorové API
# =============================================================================


@app.route("/health", methods=["GET"])
def health_check():
    """Overenie, že API server beží"""
    return jsonify(
        {
            "status": "OK",
            "message": "Senzorove API bezi spravne",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/sensor", methods=["POST"])
def add_sensor_data():
    """
    Pridanie nových senzorových dát
    Očakáva JSON s poliami: sensor_id, temperature, humidity, location atď.
    """
    try:
        # Získanie JSON dát z requestu
        data = request.get_json()

        if not data:
            return jsonify({"error": "Chýbajú JSON dáta"}), 400

        if "sensor_id" not in data:
            return jsonify({"error": "Pole 'sensor_id' je povinné"}), 400

        # Pridanie časovej pečiatky ak chýba
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat() + "Z"

        # Uloženie do MongoDB
        result = collection.insert_one(data)

        logger.info(f"Pridaný senzor: {data['sensor_id']}")

        return (
            jsonify(
                {
                    "message": "Senzorove data uspesne ulozene",
                    "sensor_id": data["sensor_id"],
                    "id": str(result.inserted_id),
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Chyba pri pridávaní dát: {e}")
        return jsonify({"error": "Chyba pri ukladani dat"}), 500


@app.route("/sensor/<sensor_id>", methods=["GET"])
def get_sensor_data(sensor_id):
    """Získanie dát konkrétneho senzora"""
    try:
        # Vyhľadanie v databáze
        sensor = collection.find_one({"sensor_id": sensor_id}, {"_id": 0})

        if not sensor:
            return jsonify({"error": f"Senzor '{sensor_id}' nebol najdeny"}), 404

        return jsonify(sensor)

    except Exception as e:
        logger.error(f"Chyba pri získavaní dát: {e}")
        return jsonify({"error": "Chyba pri nacitavani dat"}), 500


@app.route("/sensors", methods=["GET"])
def get_all_sensors():
    """
    Získanie všetkých senzorových dát
    Query parametre:
    - limit: počet záznamov (max 100)
    - location: filter podľa lokácie
    """
    try:
        # Získanie parametrov z URL
        limit = int(request.args.get("limit", 20))  # Default 20 záznamov
        if limit > 100:
            limit = 100  # Maximálne 100 záznamov

        location = request.args.get("location")

        # Vytvorenie filtra
        query_filter = {}
        if location:
            query_filter["location"] = location

        # Načítanie dát z databázy
        sensors = list(collection.find(query_filter, {"_id": 0}).limit(limit))

        # Počet všetkých záznamov
        total_count = collection.count_documents(query_filter)

        return jsonify(
            {
                "sensors": sensors,
                "count": len(sensors),
                "total_count": total_count,
                "limit": limit,
            }
        )

    except Exception as e:
        logger.error(f"Chyba pri získavaní zoznamu: {e}")
        return jsonify({"error": "Chyba pri nacitavani zoznamu"}), 500


@app.route("/sensors/search", methods=["GET"])
def search_sensors():
    """
    Vyhľadávanie senzorov podľa parametrov
    Query parametre:
    - location: lokácia senzora
    - min_temp: minimálna teplota
    - max_temp: maximálna teplota
    - min_humidity: minimálna vlhkosť
    - max_humidity: maximálna vlhkosť
    """
    try:
        # Získanie parametrov
        location = request.args.get("location")
        min_temp = request.args.get("min_temp")
        max_temp = request.args.get("max_temp")
        min_humidity = request.args.get("min_humidity")
        max_humidity = request.args.get("max_humidity")

        # Vytvorenie MongoDB query
        query = {}

        if location:
            query["location"] = location

        if min_temp or max_temp:
            query["temperature"] = {}
            if min_temp:
                query["temperature"]["$gte"] = float(min_temp)
            if max_temp:
                query["temperature"]["$lte"] = float(max_temp)

        if min_humidity or max_humidity:
            query["humidity"] = {}
            if min_humidity:
                query["humidity"]["$gte"] = float(min_humidity)
            if max_humidity:
                query["humidity"]["$lte"] = float(max_humidity)

        # Vyhľadávanie
        sensors = list(collection.find(query, {"_id": 0}).limit(50))

        return jsonify({"sensors": sensors, "count": len(sensors), "query": query})

    except ValueError as e:
        return jsonify({"error": "Neplatne ciselne hodnoty"}), 400
    except Exception as e:
        logger.error(f"Chyba pri vyhľadávaní: {e}")
        return jsonify({"error": "Chyba pri vyhladavani"}), 500


@app.route("/sensor/<sensor_id>", methods=["DELETE"])
def delete_sensor(sensor_id):
    """Zmazanie senzorových dát"""
    try:
        result = collection.delete_one({"sensor_id": sensor_id})

        if result.deleted_count == 0:
            return jsonify({"error": f"Senzor '{sensor_id}' nebol najdeny"}), 404

        logger.info(f"Zmazany senzor: {sensor_id}")
        return jsonify({"message": f"Senzor '{sensor_id}' bol uspesne zmazany"})

    except Exception as e:
        logger.error(f"Chyba pri mazaní: {e}")
        return jsonify({"error": "Chyba pri mazani"}), 500


@app.route("/sensors/bulk", methods=["POST"])
def add_bulk_sensors():
    """
    Hromadné pridávanie senzorových dát
    Očakáva JSON array s viacerými senzormi
    """
    try:
        data = request.get_json()

        if not data or not isinstance(data, list):
            return jsonify({"error": "Ocakava sa JSON array so senzormi"}), 400

        # Pridanie časovej pečiatky ku každému záznamu
        current_time = datetime.now().isoformat() + "Z"
        for item in data:
            if "timestamp" not in item:
                item["timestamp"] = current_time

        # Hromadné vloženie do databázy
        result = collection.insert_many(data)

        logger.info(f"Pridaných {len(result.inserted_ids)} senzorov")

        return (
            jsonify(
                {
                    "message": f"Úspešne pridaných {len(result.inserted_ids)} senzorov",
                    "count": len(result.inserted_ids),
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Chyba pri hromadnom pridávaní: {e}")
        return jsonify({"error": "Chyba pri hromadnom pridavani"}), 500


@app.route("/sensors/stats", methods=["GET"])
def get_sensor_stats():
    """Základné statistiky o senzorových dátach"""
    try:
        # Počet všetkých senzorov
        total_sensors = collection.count_documents({})

        # Počet senzorov podľa lokácie
        locations = list(
            collection.aggregate(
                [
                    {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )

        # Priemerné hodnoty
        avg_stats = list(
            collection.aggregate(
                [
                    {
                        "$group": {
                            "_id": None,
                            "avg_temperature": {"$avg": "$temperature"},
                            "avg_humidity": {"$avg": "$humidity"},
                            "avg_pressure": {"$avg": "$pressure"},
                        }
                    }
                ]
            )
        )

        return jsonify(
            {
                "total_sensors": total_sensors,
                "locations": locations,
                "averages": avg_stats[0] if avg_stats else {},
            }
        )

    except Exception as e:
        logger.error(f"Chyba pri získavaní štatistík: {e}")
        return jsonify({"error": "Chyba pri ziskavani statistik"}), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint nebol najdeny"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "HTTP metoda nie je povolena"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Interna chyba servera"}), 500


# =============================================================================
# SPUSTENIE SERVERA
# =============================================================================

if __name__ == "__main__":
    logger.info("Spúšťanie jednoduchého senzorového API servera...")
    logger.info(f"Server bude dostupný na: http://localhost:8080")
    logger.info(f"MongoDB: {MONGO_HOST}:{MONGO_PORT}/{DB_NAME}")
    logger.info(f"Kolekcia: {COLLECTION_NAME}")
    logger.info("")
    logger.info("Dostupné endpointy:")
    logger.info("  POST   /sensor              - Pridanie senzorových dát")
    logger.info("  GET    /sensor/<sensor_id>  - Získanie dát senzora")
    logger.info("  GET    /sensors             - Zoznam všetkých senzorov")
    logger.info("  GET    /sensors/search      - Vyhľadávanie senzorov")
    logger.info("  DELETE /sensor/<sensor_id>  - Zmazanie senzora")
    logger.info("  POST   /sensors/bulk        - Hromadné pridávanie")
    logger.info("  GET    /sensors/stats       - Základné štatistiky")
    logger.info("  GET    /health              - Health check")

    # Spustenie Flask servera
    app.run(host="0.0.0.0", port=8080, debug=True)  # Zapne debug režim pre vývoj
