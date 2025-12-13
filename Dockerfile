FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système minimales (pour éviter les warnings / problèmes réseau)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances en premier (meilleur cache Docker)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Lancer l'app Streamlit
# Remplace "app.py" par le nom exact de ton fichier si différent
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
