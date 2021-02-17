from googlemaps import Client as GoogleMaps

def compress(address):
    try:
        gmaps = GoogleMaps('AIzaSyAH-SEZ1C_8Kb1ACyPCZZpZAJKKDuWD3Ro')
        geocode_result = gmaps.geocode(address)
        return geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']
    except IndexError:
        print("Address was wrong...")
        return "null", "null"
    except Exception as e:
        print("Unexpected error occurred.", e)

