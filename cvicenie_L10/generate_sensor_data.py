#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator testovacích senzorových dát
Vytvorí CSV súbor s približne 5MB dát
"""

import csv
import random
import datetime
import os
from pathlib import Path


def generate_sensor_data(num_records=50000, output_file="sensor_test_data.csv"):
    """
    Generuje testovací CSV súbor so senzorovými dátami

    Args:
        num_records (int): Počet záznamov na vygenerovanie (50k = cca 5MB)
        output_file (str): Názov výstupného súboru
    """

    # Konfigurácia pre realistické dáta
    locations = [
        "warehouse_a",
        "warehouse_b",
        "warehouse_c",
        "office_floor1",
        "office_floor2",
        "office_floor3",
        "production_hall",
        "storage_room",
        "server_room",
        "laboratory",
        "reception",
        "cafeteria",
        "parking_garage",
        "loading_dock",
        "quality_control",
    ]

    # Typy senzorov
    sensor_types = ["temp", "humid", "pressure", "light", "motion", "air_quality"]

    # Časové rozpätie - posledných 30 dní
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=30)

    print(f"Generujem {num_records:,} záznamov senzorových dát...")
    print(
        f"Časové rozpätie: {start_time.strftime('%Y-%m-%d')} až {end_time.strftime('%Y-%m-%d')}"
    )

    # CSV hlavička
    fieldnames = [
        "sensor_id",
        "temperature",
        "humidity",
        "pressure",
        "light_level",
        "air_quality_index",
        "location",
        "timestamp",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_records):
            # Generovanie náhodného času v posledných 30 dňoch
            random_time = start_time + datetime.timedelta(
                seconds=random.randint(0, int((end_time - start_time).total_seconds()))
            )

            # Výber náhodného typu senzora a lokácie
            sensor_type = random.choice(sensor_types)
            location = random.choice(locations)
            sensor_number = random.randint(1, 99)

            # Generovanie realistických hodnôt podľa lokácie
            if location == "server_room":
                base_temp = random.uniform(18, 22)  # Chladnejšie
                base_humidity = random.uniform(45, 55)  # Nižšia vlhkosť
            elif location == "warehouse_a" or location == "warehouse_b":
                base_temp = random.uniform(15, 25)  # Skladové teploty
                base_humidity = random.uniform(50, 70)
            elif location.startswith("office"):
                base_temp = random.uniform(20, 24)  # Kancelárske teploty
                base_humidity = random.uniform(40, 60)
            elif location == "production_hall":
                base_temp = random.uniform(22, 28)  # Teplejšie od strojov
                base_humidity = random.uniform(55, 75)
            else:
                base_temp = random.uniform(18, 26)  # Štandardné
                base_humidity = random.uniform(45, 65)

            # Pridanie denných variácií (ráno chladnejšie, popoludní teplejšie)
            hour = random_time.hour
            if 6 <= hour <= 10:  # Ráno
                temp_modifier = -2
            elif 12 <= hour <= 16:  # Popoludnie
                temp_modifier = 2
            elif 18 <= hour <= 22:  # Večer
                temp_modifier = 1
            else:  # Noc
                temp_modifier = -1

            temperature = round(base_temp + temp_modifier + random.uniform(-1, 1), 1)
            humidity = round(base_humidity + random.uniform(-5, 5), 1)

            # Ostatné senzorové hodnoty
            pressure = round(random.uniform(980, 1020), 1)  # hPa
            light_level = random.randint(0, 1000)  # lux
            air_quality = random.randint(20, 200)  # AQI

            # Záznam
            record = {
                "sensor_id": f"{sensor_type}_{sensor_number:02d}",
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "light_level": light_level,
                "air_quality_index": air_quality,
                "location": location,
                "timestamp": random_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            }

            writer.writerow(record)

            # Progress indikátor
            if (i + 1) % 5000 == 0:
                print(f"  Vygenerovaných: {i + 1:,} záznamov...")

    # Informácie o výstupnom súbore
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)

    print(f"\n✅ Generovanie dokončené!")
    print(f"📁 Súbor: {output_file}")
    print(f"📊 Počet záznamov: {num_records:,}")
    print(f"💾 Veľkosť súboru: {file_size_mb:.2f} MB ({file_size:,} bytov)")

    # Ukážka prvých záznamov
    print(f"\n📋 Ukážka prvých 3 záznamov:")
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(f"  {i+1}. {row}")


def main():
    """Hlavná funkcia"""
    output_dir = Path("c:\\_Dev\\robot_dreams\\cvicenie_l10")
    output_file = output_dir / "sensor_test_data.csv"

    print("🔧 Generator testovacích senzorových dát")
    print("=" * 50)

    # Vytvorenie adresára ak neexistuje
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generovanie dát (50k záznamov = približne 5MB)
    generate_sensor_data(
        num_records=50000, output_file=str(output_file)  # Upravte podľa potreby
    )

    print(f"\n🚀 CSV súbor je pripravený na import do MongoDB cez Streamlit UI!")
    print(f"   Url: http://localhost:8501")


if __name__ == "__main__":
    main()
