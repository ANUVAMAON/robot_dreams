# Univerzálne Flask REST API s MongoDB integráciou

Tento projekt obsahuje univerzálny Flask REST API server, ktorý dokáže pracovať s ľubovoľnou štruktúrou JSON dát. API automaticky rozpozná typ dát a poskytuje pokročilé funkcie pre správu, vyhľadávanie a analýzu záznamov v MongoDB databáze.

## Funkcie

### 🔧 **Základné CRUD operácie**

#### 1. Uloženie/Aktualizácia záznamu
- **URL:** `POST /record`
- **Content-Type:** `application/json`
- **Popis:** Univerzálne uloženie ľubovoľného typu záznamu. API automaticky rozpozná ID pole.
- **Podporované ID polia:** `id`, `product_id`, `sensor_id`, `user_id`, `item_id`, `record_id`

**Príklady požiadaviek:**
```json
// Produktové dáta
{
    "product_id": "101",
    "quantity": 5,
    "price_per_unit": 15.50,
    "city": "Bratislava"
}

// Senzorové dáta
{
    "sensor_id": "temp_01",
    "temperature": 23.5,
    "humidity": 65.2,
    "unit": "celsius",
    "location": "room_1"
}

// Používateľské dáta
{
    "user_id": "john_doe",
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}
```

#### 2. Načítanie konkrétneho záznamu
- **URL:** `GET /record/<id>`
- **Popis:** Vráti záznam podľa ID (automaticky vyhľadáva vo všetkých ID poliach)
- **Príklady:** 
  - `GET /record/101` (produktové ID)
  - `GET /record/temp_01` (senzorové ID)
  - `GET /record/john_doe` (používateľské ID)

#### 3. Zmazanie záznamu
- **URL:** `DELETE /record/<id>`
- **Popis:** Zmaže záznam podľa ID
- **Príklad:** `DELETE /record/101`

### 📊 **Kolekcie a vyhľadávanie**

#### 4. Načítanie všetkých záznamov s pokročilými funkciami
- **URL:** `GET /records`
- **Query parametre:**
  - `limit` - max počet záznamov (default: 100, max: 1000)
  - `skip` - počet záznamov na preskočenie (pagination)
  - `fields` - vybrané polia (čiarkami oddelené)
  - `sort_by` - pole na triedenie
  - `sort_order` - `asc`/`desc` (default: asc)

**Príklady:**
```bash
GET /records?limit=10&skip=20                    # Pagination
GET /records?fields=product_id,price_per_unit    # Vybrané polia
GET /records?sort_by=price_per_unit&sort_order=desc  # Triedenie
```

#### 5. Pokročilé vyhľadávanie
- **URL:** `GET /search`
- **Query parametre:**
  - `q` - textové vyhľadávanie (vo všetkých string poliach)
  - `<field_name>` - presný filter podľa poľa
  - `min_<field_name>` - minimálna hodnota
  - `max_<field_name>` - maximálna hodnota

**Príklady:**
```bash
GET /search?q=Bratislava                          # Textové vyhľadávanie
GET /search?city=Bratislava                       # Filter podľa mesta
GET /search?min_price_per_unit=10&max_price_per_unit=50  # Cenový rozsah
GET /search?quantity=5&city=Bratislava            # Kombinácia filtrov
```

#### 6. Hromadné vkladanie
- **URL:** `POST /bulk`
- **Content-Type:** `application/json`
- **Popis:** Vloženie viacerých záznamov naraz (JSON array)

**Príklad:**
```json
[
    {"product_id": "101", "quantity": 5, "price_per_unit": 15.50, "city": "Bratislava"},
    {"product_id": "102", "quantity": 12, "price_per_unit": 5.00, "city": "Košice"},
    {"product_id": "103", "quantity": 3, "price_per_unit": 45.99, "city": "Bratislava"}
]
```

### 🔍 **Metadata a diagnostika**

#### 7. Analýza štruktúry dát
- **URL:** `GET /schema`
- **Popis:** Analyzuje štruktúru dát v kolekcii - vráti polia, ich typy a príklady hodnôt
- **Použitie:** Ideálne na pochopenie štruktúry po importe nových dát

#### 8. Health Check
- **URL:** `GET /health`
- **Popis:** Overuje stav API servera a pripojenie k databáze
- **Odpoveď:** JSON s informáciami o stave a časovej pečiatke

## Konfigurácia

Aplikácia používa environmentálne premenné na konfiguráciu:

- `MONGO_HOST` - hostname MongoDB servera (default: `localhost`)
- `MONGO_PORT` - port MongoDB servera (default: `27017`)
- `DB_NAME` - názov databázy (default: `robot_dreams_db`)
- `COLLECTION_NAME` - názov kolekcie (default: `cvicenie_lekcia_10`)

## Spustenie pomocou Docker Compose

1. Spustite celý stack (MongoDB + univerzálne Flask API + Streamlit CSV importer):
```bash
podman-compose up --build
# alebo
docker-compose up --build
```

2. **Služby budú dostupné na:**
   - 🌐 **Flask API:** `http://localhost:8080`
   - 🗄️ **MongoDB:** `localhost:27017`
   - 📊 **Streamlit UI:** `http://localhost:8501`

## Lokálne spustenie (bez Docker)

1. Naištalujte závislosti:
```bash
pip install -r requirements.txt
```

2. Spustite MongoDB lokálne alebo nastavte premenné prostredia

3. Spustite Flask aplikáciu:
```bash
python flask_api.py
```

## Testovanie

### PowerShell (Windows)

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8080/health"

# Analýza štruktúry dát
Invoke-RestMethod -Uri "http://localhost:8080/schema"

# Pridanie produktu
Invoke-RestMethod -Uri "http://localhost:8080/record" -Method POST -ContentType "application/json" -Body '{"product_id":"101","quantity":5,"price_per_unit":15.50,"city":"Bratislava"}'

# Získanie produktu
Invoke-RestMethod -Uri "http://localhost:8080/record/101"

# Hromadné vkladanie
$bulkData = '[{"product_id":"102","quantity":12,"price_per_unit":5.00,"city":"Kosice"},{"product_id":"103","quantity":3,"price_per_unit":45.99,"city":"Bratislava"}]'
Invoke-RestMethod -Uri "http://localhost:8080/bulk" -Method POST -ContentType "application/json" -Body $bulkData

# Vyhľadávanie podľa mesta
Invoke-RestMethod -Uri "http://localhost:8080/search?city=Bratislava"

# Cenový rozsah
Invoke-RestMethod -Uri "http://localhost:8080/search?min_price_per_unit=10&max_price_per_unit=50"

# Všetky záznamy s triedením
Invoke-RestMethod -Uri "http://localhost:8080/records?sort_by=price_per_unit&sort_order=desc"

# Zmazanie záznamu
Invoke-RestMethod -Uri "http://localhost:8080/record/101" -Method DELETE
```

### cURL (Linux/Mac)

```bash
# Health check
curl http://localhost:8080/health

# Pridanie záznamu
curl -X POST http://localhost:8080/record \
  -H "Content-Type: application/json" \
  -d '{"product_id":"101","quantity":5,"price_per_unit":15.50,"city":"Bratislava"}'

# Získanie záznamu
curl http://localhost:8080/record/101

# Vyhľadávanie
curl "http://localhost:8080/search?city=Bratislava&min_price_per_unit=10"

# Všetky záznamy s limitom
curl "http://localhost:8080/records?limit=5&sort_by=price_per_unit"

# Zmazanie záznamu
curl -X DELETE http://localhost:8080/record/101
```

### Automatizované testovanie

```bash
# Spustite test script (ak existuje)
python test_api.py
```

## 🎯 Práca s REST API - Podrobný návod

### Spustenie celého systému

1. **Spustenie cez Docker/Podman:**
```bash
podman-compose up --build
# alebo
docker-compose up --build
```

2. **Overenie, že všetky služby bežia:**
```powershell
# Health check API
Invoke-RestMethod -Uri "http://localhost:8080/health"

# Test Streamlit UI
Start-Process "http://localhost:8501"
```

### Základné workflow s API

#### 1. Analýza existujúcich dát
```powershell
# Pozrieme si štruktúru dát v databáze
Invoke-RestMethod -Uri "http://localhost:8080/schema"

# Získame počet záznamov
Invoke-RestMethod -Uri "http://localhost:8080/records?limit=1" | ConvertTo-Json
```

#### 2. Pridávanie jednotlivých záznamov
```powershell
# Senzorový záznam
$sensorData = @{
    sensor_id = "temp_01"
    temperature = 23.5
    humidity = 65.2
    location = "warehouse_a"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/record" -Method POST -ContentType "application/json" -Body $sensorData

# Produktový záznam  
$productData = @{
    product_id = "101"
    quantity = 5
    price_per_unit = 15.50
    city = "Bratislava"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/record" -Method POST -ContentType "application/json" -Body $productData
```

#### 3. Hromadné operácie
```powershell
# Pripravíme viacero záznamov
$bulkData = @(
    @{ sensor_id = "temp_02"; temperature = 21.3; humidity = 58.1; location = "office_floor1" }
    @{ sensor_id = "humid_01"; temperature = 24.7; humidity = 72.4; location = "warehouse_b" }
    @{ sensor_id = "motion_03"; temperature = 19.8; humidity = 45.2; location = "server_room" }
) | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/bulk" -Method POST -ContentType "application/json" -Body $bulkData
```

#### 4. Pokročilé vyhľadávanie
```powershell
# Textové vyhľadávanie
Invoke-RestMethod -Uri "http://localhost:8080/search?q=warehouse"

# Filter podľa teploty
Invoke-RestMethod -Uri "http://localhost:8080/search?min_temperature=20&max_temperature=25"

# Kombinácia filtrov
Invoke-RestMethod -Uri "http://localhost:8080/search?location=warehouse_a&min_humidity=60"

# Časové vyhľadávanie (ak máte timestamp pole)
Invoke-RestMethod -Uri "http://localhost:8080/search?min_timestamp=2025-11-01T00:00:00Z"
```

#### 5. Paginácia a triedenie
```powershell
# Prvých 10 záznamov
Invoke-RestMethod -Uri "http://localhost:8080/records?limit=10"

# Druhá stránka (preskočíme prvých 10)
Invoke-RestMethod -Uri "http://localhost:8080/records?limit=10&skip=10"

# Triedenie podľa teploty (zostupne)
Invoke-RestMethod -Uri "http://localhost:8080/records?sort_by=temperature&sort_order=desc&limit=5"

# Len vybrané polia
Invoke-RestMethod -Uri "http://localhost:8080/records?fields=sensor_id,temperature,location&limit=5"
```

#### 6. Aktualizácia a mazanie
```powershell
# Aktualizácia záznamu (POST s existujúcim ID prepíše záznam)
$updatedData = @{
    sensor_id = "temp_01"
    temperature = 25.1
    humidity = 67.3
    location = "warehouse_a"
    status = "updated"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/record" -Method POST -ContentType "application/json" -Body $updatedData

# Zmazanie záznamu
Invoke-RestMethod -Uri "http://localhost:8080/record/temp_01" -Method DELETE
```

## 🔧 Generovanie testovacích dát

### Automatický generátor

V projekte je k dispozícii skript na generovanie realistických testovacích dát:

```bash
# Spustenie generátora (vytvorí cca 5MB súbor)
python generate_sensor_data.py
```

### Konfigurácia generátora

Môžete upraviť parametre v `generate_sensor_data.py`:

```python
# Počet záznamov (70k = cca 5MB)
num_records = 70000

# Typy senzorov
sensor_types = ["temp", "humid", "pressure", "light", "motion", "air_quality"]

# Lokácie
locations = [
    "warehouse_a", "warehouse_b", "warehouse_c",
    "office_floor1", "office_floor2", "office_floor3",
    "production_hall", "storage_room", "server_room",
    "laboratory", "reception", "cafeteria"
]

# Časové rozpätie
days_back = 30  # Posledných 30 dní
```

### Vlastné testovací dáta

#### Manuálne vytvorenie CSV súboru:
```csv
sensor_id,temperature,humidity,location,timestamp
temp_01,23.5,65.2,warehouse_a,2025-11-09T10:30:00Z
humid_02,21.3,58.7,office_floor1,2025-11-09T10:31:00Z
motion_03,19.8,45.1,server_room,2025-11-09T10:32:00Z
```

#### Import cez Streamlit UI:
1. Otvorte `http://localhost:8501`
2. Nahrajte CSV súbor
3. Zvoľte mapovanie stĺpcov
4. Kliknite "Import to MongoDB"

#### Import cez API (ak by sme pridali CSV endpoint):
```powershell
# Hypothetický CSV import endpoint
Invoke-RestMethod -Uri "http://localhost:8080/import/csv" -Method POST -InFile "sensor_test_5mb.csv"
```

### Typy testovacích scenárov

#### 1. Výkonnostné testovanie:
```powershell
# Test s veľkým množstvom dát
Measure-Command { 
    Invoke-RestMethod -Uri "http://localhost:8080/records?limit=1000" 
}

# Test vyhľadávania v rozsahu
Measure-Command { 
    Invoke-RestMethod -Uri "http://localhost:8080/search?min_temperature=20&max_temperature=25" 
}
```

#### 2. Stresové testovanie:
```powershell
# Viacero súčasných requestov
1..10 | ForEach-Object -Parallel {
    Invoke-RestMethod -Uri "http://localhost:8080/health"
} -ThrottleLimit 5
```

#### 3. Testovanie chybových stavov:
```powershell
# Neexistujúce ID
try {
    Invoke-RestMethod -Uri "http://localhost:8080/record/neexistuje"
} catch {
    Write-Host "Očakávaná chyba: $($_.Exception.Message)"
}

# Neplatný JSON
try {
    Invoke-RestMethod -Uri "http://localhost:8080/record" -Method POST -ContentType "application/json" -Body "neplatny json"
} catch {
    Write-Host "Očakávaná chyba: $($_.Exception.Message)"
}
```

## Štruktúra MongoDB

API funguje s akoukoľvek štruktúrou JSON dát. Automaticky detekuje ID polia:
- `id`, `product_id`, `sensor_id`, `user_id`, `order_id`, `_id` atď.

### Príklady dát

**Produkty:**
```json
{
  "_id": ObjectId("..."),
  "product_id": "101",
  "quantity": 5,
  "price_per_unit": 15.50,
  "city": "Bratislava",
  "timestamp": "2024-12-18T10:30:00Z"
}
```

**Senzory:**
```json
{
  "_id": ObjectId("..."),
  "sensor_id": "temp_01",
  "temperature": 23.5,
  "humidity": 65.2,
  "location": "warehouse_a",
  "timestamp": "2024-12-18T10:30:00Z"
}
```

**Používatelia:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "user123",
  "name": "Janko Hrasko",
  "email": "janko@example.com",
  "timestamp": "2024-12-18T10:30:00Z"
}
```

**Poznámky:** 
- `_id` pole sa automaticky odstraňuje z API odpovedí
- API automaticky pridá `timestamp` ak nie je uvedený

## Bezpečnosť a Error Handling

- API obsahuje error handling pre databázové chyby
- Timeout na MongoDB pripojenie (5 sekúnd)
- Validácia JSON dát v POST requestoch
- Automatické testovanie pripojenia k databáze

## 💡 Tipy a triky pre prácu s API

### Debug a monitoring
```powershell
# Sledovanie logov Docker kontajnera
podman logs -f rest_api_server

# Overenie MongoDB pripojenia
podman exec -it cvicenie_l10-mongodb-1 mongosh --eval "db.adminCommand('ping')"

# Počet dokumentov v kolekcii
Invoke-RestMethod -Uri "http://localhost:8080/records?limit=1" | Select-Object -ExpandProperty total_count
```

### Optimalizácia výkonu
```powershell
# Použitie indexov (ak sú nastavené)
Invoke-RestMethod -Uri "http://localhost:8080/search?sensor_id=temp_01"  # Rýchle (ID field)
Invoke-RestMethod -Uri "http://localhost:8080/records?sort_by=timestamp&limit=100"  # Pomalšie bez indexu

# Obmedzenie polí pre menší network traffic
Invoke-RestMethod -Uri "http://localhost:8080/records?fields=sensor_id,temperature&limit=100"
```

### Backup a export dát
```bash
# MongoDB dump (v Docker kontajneri)
podman exec cvicenie_l10-mongodb-1 mongodump --db robot_dreams_db --collection cvicenie_lekcia_10 --out /tmp/backup

# Export cez API (všetky dáta)
Invoke-RestMethod -Uri "http://localhost:8080/records?limit=100000" | ConvertTo-Json -Depth 10 | Out-File "api_export.json"
```

## 🚀 Rozšírenia a ďalší vývoj

### Možné vylepšenia API:

1. **CSV Import/Export endpoint:**
   ```python
   @app.route('/import/csv', methods=['POST'])
   @app.route('/export/csv', methods=['GET'])
   ```

2. **Agregačné funkcie:**
   ```python
   @app.route('/analytics/avg/<field>')
   @app.route('/analytics/count_by/<field>')
   ```

3. **Real-time updates (WebSocket):**
   ```python
   from flask_socketio import SocketIO
   # Live updates pri pridaní nových dát
   ```

4. **Validácia dát podľa schémy:**
   ```python
   from jsonschema import validate
   # Automatická validácia na základe detekovanej štruktúry
   ```

### Rozšírenia infrastruktúry:

- **Redis cache:** Pre rýchlejšie vyhľadávanie
- **Elasticsearch:** Pre pokročilé full-text search
- **Grafana dashboards:** Pre vizualizáciu dát
- **API Gateway:** Pre rate limiting a autentifikáciu
- **Load balancer:** Pre vysokú dostupnosť

### Monitoring a bezpečnosť:

- **Prometheus metrics:** Sledovanie výkonu API
- **JWT autentifikácia:** Zabezpečenie endpointov
- **HTTPS:** SSL certifikáty pre produkciu
- **Input sanitization:** Ochrana pred injection útokmi
- **Rate limiting:** Ochrana pred DDoS útokmi

Univerzálne API poskytuje solídnu bázu pre ďalší vývoj a môže byť jednoducho rozšírené podľa konkrétnych potrieb projektu.