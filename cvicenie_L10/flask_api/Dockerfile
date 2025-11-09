# Základný image
FROM python:3.12-slim

# Definuje pracovný adresár pre aplikáciu
WORKDIR /app

# Kopíruje server skript
COPY flask_api.py /app

# Inštalácia kľúčových závislostí: webový framework a databázový ovládač
RUN pip install flask pymongo

# Exponuje aplikačný port
EXPOSE 8080

# Entrypoint: Spustí Flask server
CMD ["python", "flask_api.py"]