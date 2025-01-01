# Używamy oficjalnego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki z zależnościami
COPY requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Tworzymy katalog templates
RUN mkdir -p /app/templates

# Kopiujemy pliki aplikacji
COPY youtube_down_python.py .
COPY app.py .
COPY templates/index.html /app/templates/

# Tworzymy katalog na pobrane pliki
RUN mkdir -p /app/downloads

# Ustawiamy uprawnienia dla katalogu downloads
RUN chmod 777 /app/downloads

# Eksponujemy port dla aplikacji Flask
EXPOSE 5000

# Ustawiamy zmienne środowiskowe
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Uruchamiamy aplikację Flask
CMD ["python", "app.py"] 