# app-youtube-subtitles-downloader-python

# Zbuduj obraz
docker build -t youtube-transcripts-web .

# Uruchom kontener
docker run -p 5050:5000 -v $(pwd)/downloads:/app/downloads youtube-transcripts-web