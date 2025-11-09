# Základný image
FROM node:18-slim

# Definuje pracovný adresár pre aplikáciu
WORKDIR /usr/src/app

# Kopíruje server skript
COPY api_server.js .

# Inštalácia kľúčových závislostí: webový framework a databázový ovládač
RUN npm install express mongodb

# Exponuje aplikačný port
EXPOSE 3000

# Entrypoint: Spustí Node.js proces
CMD ["node", "api_server.js"]