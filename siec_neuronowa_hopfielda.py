import requests
import cx_Oracle
from datetime import datetime


# Funkcja łącząca się z bazą danych Oracle
def connect_to_db():
    # Dane do połączenia
    username = ''
    password = ''
    hostname = '213.184.8.44'
    port = '1521'
    sid = 'orcl'

    # Tworzymy DSN (Data Source Name)
    dsn_tns = cx_Oracle.makedsn(hostname, port, sid=sid)

    # Łączymy się z bazą danych
    connection = cx_Oracle.connect(username, password, dsn_tns)
    return connection


# Funkcja do pobierania danych z API pogodowego (OpenWeatherMap)
def fetch_weather_data():
    api_key = "277a453f4257c0f070c6dee68c249aa4"  # Twój klucz API
    city = "Warszawa"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # Sprawdzamy, czy dane są poprawne
        if data["main"].get("temp") is None or data["wind"].get("speed") is None:
            print("Błąd: Brak wymaganych danych pogodowych")
            return None

        return {
            "temperatura": data["main"]["temp"] - 273.15,  # Konwersja z Kelvinów na stopnie Celsjusza
            "wilgotnosc": data["main"]["humidity"],
            "predkosc_wiatru": data["wind"]["speed"],
            "cisnienie": data["main"]["pressure"],
            "data": datetime.now().date()
        }
    else:
        print(f"Błąd podczas pobierania danych z API. Status kodu: {response.status_code}")
        return None


# Funkcja do zapisywania danych pogodowych w bazie danych
def save_weather_data(weather_data):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        # Sprawdzenie, czy lokalizacja już istnieje
        cursor.execute("SELECT id FROM Lokacje WHERE nazwa = 'Warszawa'")
        result = cursor.fetchone()

        if result:
            lokalizacja_id = result[0]
        else:
            # Jeśli lokalizacja nie istnieje, dodajemy ją do tabeli Lokacje z użyciem sekwencji
            cursor.execute("""
                INSERT INTO Lokacje (id, nazwa, szerokosc_geograficzna, dlugosc_geograficzna)
                VALUES (Lokacje_SEQ.NEXTVAL, 'Warszawa', 52.2298, 21.0118)
            """)
            connection.commit()
            # Pobieramy id nowo dodanej lokalizacji
            cursor.execute("SELECT Lokacje_SEQ.CURRVAL FROM DUAL")
            lokalizacja_id = cursor.fetchone()[0]

        # Zapisanie danych pogodowych
        cursor.execute("""
            INSERT INTO Pogoda (id, lokalizacja_id, data, temperatura, wilgotnosc, predkosc_wiatru, cisnienie)
            VALUES (Pogoda_SEQ.NEXTVAL, :lokalizacja_id, :data, :temperatura, :wilgotnosc, :predkosc_wiatru, :cisnienie)
        """, {
            'lokalizacja_id': lokalizacja_id,
            'data': weather_data['data'],
            'temperatura': round(float(weather_data['temperatura']), 2),
            'wilgotnosc': round(float(weather_data['wilgotnosc']), 2),
            'predkosc_wiatru': round(float(weather_data['predkosc_wiatru']), 2),
            'cisnienie': round(float(weather_data['cisnienie']), 2)
        })
        connection.commit()
        print(f"Dane pogodowe dla Warszawy na dzień {weather_data['data']} zostały zapisane.")

    except Exception as e:
        print(f"Błąd podczas zapisywania danych: {e}")
    finally:
        cursor.close()
        connection.close()


# Funkcja do zapisywania prognozy pogody w bazie danych
# Funkcja do zapisywania prognozy pogody w bazie danych
# Funkcja do zapisywania prognozy pogody w bazie danych
def save_weather_forecast(weather_data):
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        # Sprawdzenie, czy lokalizacja już istnieje
        cursor.execute("SELECT id FROM Lokacje WHERE nazwa = 'Warszawa'")
        result = cursor.fetchone()

        if result:
            lokalizacja_id = result[0]
        else:
            # Jeśli lokalizacja nie istnieje, dodajemy ją do tabeli Lokacje z użyciem sekwencji
            cursor.execute(""" 
                INSERT INTO Lokacje (id, nazwa, szerokosc_geograficzna, dlugosc_geograficzna)
                VALUES (Lokacje_SEQ.NEXTVAL, 'Warszawa', 52.2298, 21.0118)
            """)
            connection.commit()
            # Pobieramy id nowo dodanej lokalizacji
            cursor.execute("SELECT Lokacje_SEQ.CURRVAL FROM DUAL")
            lokalizacja_id = cursor.fetchone()[0]

        # Sprawdzenie wartości przed zapisaniem do bazy
        przewidywana_temperatura = round(float(weather_data['temperatura']), 2)
        przewidywana_wilgotnosc = round(float(weather_data['wilgotnosc']), 2)
        przewidywana_predkosc_wiatru = round(float(weather_data['predkosc_wiatru']), 2)
        przewidywane_cisnienie = round(float(weather_data['cisnienie']), 2)

        # Jeśli którakolwiek wartość jest zbyt duża, zainicjuj odpowiednią reakcję
        if (przewidywana_temperatura > 999.99 or przewidywana_wilgotnosc > 100.0 or
            przewidywana_predkosc_wiatru > 200.0 or przewidywane_cisnienie > 2000.0):
            print("Błąd: Wartość przekracza dozwolony zakres")
            return

        # Zapisanie prognozy
        cursor.execute("""
            INSERT INTO Prognozy (id, lokalizacja_id, data_prognozy, przewidywana_temperatura, 
                                  przewidywana_wilgotnosc, przewidywana_predkosc_wiatru, przewidywane_cisnienie)
            VALUES (Prognozy_SEQ.NEXTVAL, :lokalizacja_id, :data_prognozy, :przewidywana_temperatura, 
                    :przewidywana_wilgotnosc, :przewidywana_predkosc_wiatru, :przewidywane_cisnienie)
        """, {
            'lokalizacja_id': lokalizacja_id,
            'data_prognozy': weather_data['data'],
            'przewidywana_temperatura': przewidywana_temperatura,
            'przewidywana_wilgotnosc': przewidywana_wilgotnosc,
            'przewidywana_predkosc_wiatru': przewidywana_predkosc_wiatru,
            'przewidywane_cisnienie': przewidywane_cisnienie
        })
        connection.commit()
        print(f"Prognoza pogody dla Warszawy na dzień {weather_data['data']} została zapisana.")

    except Exception as e:
        print(f"Błąd podczas zapisywania prognozy: {e}")
    finally:
        cursor.close()
        connection.close()

# Główna funkcja, która pobiera dane i zapisuje je w bazie
if __name__ == "__main__":
    weather_data = fetch_weather_data()
    if weather_data:
        save_weather_data(weather_data)
        save_weather_forecast(weather_data)
