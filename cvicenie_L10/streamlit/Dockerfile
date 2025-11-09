# Základný image
FROM python:3.12-slim

# Konfigurácia Streamlit pre Docker prostredie
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Definuje pracovný adresár
WORKDIR /app

# Kopíruje hlavnú aplikáciu
COPY app.py /app/

# Inštalácia kľúčových závislostí: UI framework, DB ovládač, dátový nástroj
RUN pip install --upgrade pip
RUN pip install streamlit pymongo pandas
# Exponuje aplikačný port
EXPOSE 8501

# Entrypoint: Spustí Streamlit server
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]