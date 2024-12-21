from pytube import YouTube, Playlist
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import requests
from bs4 import BeautifulSoup

def get_video_id(url):
    """Extracts video ID from various YouTube URL formats"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url:
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'embed' in url:
            return url.split('/')[-1].split('?')[0]
    return url  # jeśli to samo ID zostało podane

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.replace(' - YouTube', '')
        return title
    except Exception as e:
        print(f"Nie udało się pobrać tytułu, używam ID filmu: {e}")
        return video_id

def format_transcript_as_story(transcript):
    """Konwertuje napisy na ciągły tekst w formie opowiadania"""
    story = []
    for entry in transcript:
        # Pobierz sam tekst, pomijając znaczniki czasu
        text = entry['text'].strip()
        # Usuń niepotrzebne znaki nowej linii i wielokrotne spacje
        text = ' '.join(text.split())
        story.append(text)
    
    # Połącz wszystkie fragmenty tekstu w jeden ciągły tekst
    return ' '.join(story)

def download_transcripts(video_ids):
    for video_url in video_ids:
        try:
            video_id = get_video_id(video_url)
            
            try:
                video_title = get_video_title(video_id)
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
                print(f"\nPrzetwarzanie filmu: {video_title}")
            except Exception as e:
                print(f"Nie udało się pobrać tytułu, używam ID filmu: {e}")
                video_title = video_id
                safe_title = video_id

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pl'])
                language_code = 'pl'
                print(f"Znaleziono polskie napisy")
            except:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    language_code = 'en'
                    print(f"Znaleziono angielskie napisy")
                except:
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        language_code = 'auto'
                        print(f"Znaleziono automatyczne napisy")
                    except Exception as e:
                        print(f"❌ Nie udało się pobrać napisów dla filmu '{video_title}': {e}")
                        continue

            # Formatuj napisy jako opowiadanie
            story_text = format_transcript_as_story(transcript)
            
            # Zapisz w dwóch formatach - txt (opowiadanie) i srt (napisy z czasami)
            # Format TXT (opowiadanie)
            txt_filename = f"{safe_title}_{language_code}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as file:
                file.write(story_text)
            
            # Format SRT (oryginalny z czasami)
            formatter = SRTFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            srt_filename = f"{safe_title}_{language_code}.srt"
            with open(srt_filename, 'w', encoding='utf-8') as file:
                file.write(formatted_transcript)
                
            print(f"✓ Zapisano pliki:")
            print(f"  - Tekst ciągły: {txt_filename}")
            print(f"  - Napisy z czasami: {srt_filename}")
            print(f"  Tytuł filmu: {video_title}")
            print(f"  Język napisów: {language_code}")

        except Exception as e:
            print(f"❌ Błąd podczas przetwarzania {video_url}: {e}")
            print(f"Typ błędu: {type(e)}")
            import traceback
            print(traceback.format_exc())

def get_video_ids_from_playlist(url):
    """Pobiera listę URL filmów z playlisty lub pojedynczego filmu"""
    try:
        if 'playlist' in url or '&list=' in url:
            print("Wykryto playlistę, pobieram listę filmów...")
            playlist = Playlist(url)
            # Upewnij się, że playlista nie jest pusta
            if not playlist.video_urls:
                raise Exception("Nie znaleziono filmów w playliście")
            print(f"Znaleziono {len(playlist.video_urls)} filmów w playliście")
            return playlist.video_urls
        else:
            print("Wykryto pojedynczy film")
            return [url]
    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania URL: {e}")
        print("Próbuję przetworzyć jako pojedynczy film...")
        return [url]

if __name__ == "__main__":
    url = input("Podaj URL playlisty lub filmu YouTube: ")
    try:
        video_ids = get_video_ids_from_playlist(url)
        print(f"\nRozpoczynam pobieranie {len(video_ids)} filmów...")
        download_transcripts(video_ids)
        print("\nZakończono pobieranie wszystkich filmów!")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
