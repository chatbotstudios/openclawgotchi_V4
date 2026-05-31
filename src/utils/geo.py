import requests
import logging

log = logging.getLogger("Utils.Geo")

def get_ip_location():
    """Fetch latitude and longitude based on current public IP."""
    try:
        # We use ip-api.com as it is free for non-commercial use and no key required
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city")
            log.info(f"📍 IP-Geolocation Success: {city} ({lat}, {lon})")
            return lat, lon
        else:
            log.warning(f"IP-Geolocation failed: {data.get('message')}")
            return None
    except Exception as e:
        log.error(f"IP-Geolocation error: {e}")
        return None
