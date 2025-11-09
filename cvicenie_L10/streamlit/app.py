import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os
import io
import time

# --- Konfigurácia z premenných prostredia ---
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
DB_NAME = os.getenv("DB_NAME", "robot_dreams_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "cvicenie_lekcia_10")


def connect_to_mongo(host, port, db_name, collection_name, max_retries=10):
    """Vytvorí pripojenie k MongoDB s opakovanými pokusmi."""
    st.info(f"Pripájam sa k MongoDB na adrese: {host}:{port}...")
    for attempt in range(max_retries):
        try:
            client = MongoClient(host, port, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")  # Vynúti pripojenie
            db = client[db_name]
            collection = db[collection_name]
            st.success("Úspešne pripojené k MongoDB!")
            return client, collection
        except Exception as e:
            st.warning(
                f"Pokus {attempt + 1}/{max_retries}: Nepodarilo sa pripojiť. Čakám 5 sekúnd."
            )
            time.sleep(5)

    st.error(
        "Nepodarilo sa pripojiť k MongoDB po viacerých pokusoch. Skontrolujte službu `mongodb`."
    )
    return None, None


def import_csv_to_mongo(uploaded_file, collection):
    """Načíta dáta z nahraného CSV súboru, transformuje ich a uloží."""

    # 1. Načítanie a Transformácia dát pomocou Pandas
    try:
        # Čítanie nahraného súboru do DataFrame
        df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))

        st.subheader("Pôvodné dáta (prvých 5 riadkov):")
        st.dataframe(df.head())

        # Konverzia DataFrame na zoznam slovníkov
        data_to_insert = df.to_dict("records")

    except Exception as e:
        st.error(f"Chyba pri spracovaní CSV súboru: {e}")
        return

    # 2. Vloženie dát do MongoDB
    try:
        if data_to_insert:
            result = collection.insert_many(data_to_insert)
            st.success(
                f"Dáta boli úspešne vložené do MongoDB! Počet záznamov: {len(result.inserted_ids)}"
            )

            st.subheader("Transformované dáta (prvých 5 záznamov v DB):")
            # MongoDB automaticky pridáva _id, čo môžeme skontrolovať
            inserted_docs = collection.find().limit(5)
            st.json(list(inserted_docs))
        else:
            st.warning("CSV súbor neobsahuje žiadne dáta na vloženie.")

    except Exception as e:
        st.error(f"Vyskytla sa chyba počas vkladania do MongoDB: {e}")


# --- Streamlit UI ---

st.set_page_config(page_title="Import dát do MongoDB", layout="centered")

st.title("Import dát do MongoDB (Streamlit UI)")
st.markdown(
    "Nahrajte CSV súbor pre načítanie, transformáciu a uloženie dát do databázy."
)
st.markdown(f"**Cieľ:** Databáza `{DB_NAME}`, Kolekcia `{COLLECTION_NAME}`")

# Vytvorenie pripojenia (Streamlit cachuje túto funkciu)
client, collection = connect_to_mongo(MONGO_HOST, MONGO_PORT, DB_NAME, COLLECTION_NAME)

if collection is not None:
    uploaded_file = st.file_uploader("Vyberte CSV súbor", type=["csv"])

    if uploaded_file is not None:
        st.success(f"Súbor '{uploaded_file.name}' bol úspešne nahraný.")

        # Tlačidlo pre spustenie importu
        if st.button(
            "Importovať dáta do MongoDB",
            help="Vymaže existujúce dáta v cieľovej kolekcii a vloží nové.",
        ):
            with st.spinner("Spracúvam a vkladám dáta..."):
                import_csv_to_mongo(uploaded_file, collection)
            st.balloons()
            st.success("Import bol dokončený!")

else:
    st.error("Aplikácia nemôže pokračovať bez pripojenia k MongoDB.")
