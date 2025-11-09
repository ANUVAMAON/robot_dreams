const express = require('express');
const { MongoClient } = require('mongodb');

// --- Konfigurácia prostredia ---
const MONGO_HOST = process.env.MONGO_HOST || 'localhost';
const MONGO_PORT = process.env.MONGO_PORT || 27017;
const API_PORT = process.env.API_PORT || 3000;
const DB_NAME = "mydatabase";
const COLLECTION_NAME = "sales";

const MONGO_URI = `mongodb://${MONGO_HOST}:${MONGO_PORT}`;

const app = express();

// Parsuje prichádzajúci JSON payload
app.use(express.json());

let db;

// Inicializácia DB pripojenia s kritickým pathom
async function connectToMongo() {
    console.log(`Pripájam sa k MongoDB na adrese: ${MONGO_URI}`);
    try {
        const client = new MongoClient(MONGO_URI);
        await client.connect();
        db = client.db(DB_NAME);
        console.log("MongoDB pripojenie pre API bolo úspešne inicializované!");
    } catch (err) {
        console.error("Fatálna chyba pri pripojení k MongoDB:", err.message);
        // Kritický exit, ak DB nie je dostupná (zlyhanie spustenia)
        process.exit(1); 
    }
}

// --- REST API Endpointy ---

// GET /data: Vráti celý dataset z kolekcie 'sales'
app.get('/data', async (req, res) => {
    if (!db) {
        return res.status(503).json({ error: "Databázová služba je nedostupná." });
    }
    
    try {
        // Query na získanie všetkých dokumentov
        const data = await db.collection(COLLECTION_NAME).find({}).toArray();
        res.status(200).json(data);
    } catch (err) {
        console.error("Chyba DB operácie:", err);
        res.status(500).json({ error: 'Interná chyba servera (DB Read Error).' });
    }
});

// GET /status: Health check endpoint
app.get('/status', (req, res) => {
    const dbStatus = db ? "Pripojené" : "Odpojené";
    res.status(200).json({ 
        status: "Online",
        database: dbStatus,
        service: "REST API Server"
    });
});

// Spustenie hlavného procesu servera
connectToMongo().then(() => {
    app.listen(API_PORT, () => {
        console.log(`REST API Server beží na porte ${API_PORT}. Externý port: 8080`);
    });
});