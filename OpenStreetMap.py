import requests
import urllib.parse

# Configuración de APIs gratuitas de OpenStreetMap
GEOCODE_API = "https://nominatim.openstreetmap.org/search"
ROUTE_API = "http://router.project-osrm.org/route/v1/driving/"

def obtener_coords(direccion):
    """Convierte un nombre de lugar en coordenadas (lon, lat)"""
    # Cambiado a un User-Agent exclusivo para saltar bloqueos de seguridad del servidor OSM
    headers = {'User-Agent': 'Evaluacion2_DRY7122_DuocUC_UniqueApp_v100'} 
    params = {'q': direccion, 'format': 'json', 'limit': 1}
    try:
        response = requests.get(GEOCODE_API, params=params, headers=headers).json()
        if response:
            return response[0]['lon'], response[0]['lat'], response[0]['display_name']
    except Exception as e:
        print(f"Error al conectar con la API de coordenadas: {e}")
        return None
    return None

while True:
    print("\n=============================================")
    orig = input("Starting Location: ")
    if orig.lower() in ["quit", "q"]: 
        break
    dest = input("Destination: ")
    if dest.lower() in ["quit", "q"]: 
        break

    # 1. Obtener coordenadas de origen y destino (RELLENADO Y COMPLETADO)
    coords_orig = obtener_coords(orig)
    coords_dest = obtener_coords(dest)
    
    if not coords_orig or not coords_dest:
        print("\n**********************************************")
        print("Error: No se pudo encontrar una de las ubicaciones.")
        print("**********************************************\n")
        continue

    # 2. Solicitar la ruta a OSRM (Formato: lon,lat;lon,lat)
    puntos = f"{coords_orig[0]},{coords_orig[1]};{coords_dest[0]},{coords_dest[1]}"
    
    # Pedimos steps=true para obtener las maniobras (instrucciones)
    url_ruta = f"{ROUTE_API}{puntos}?overview=false&steps=true&alternatives=false"
    
    try:
        json_data = requests.get(url_ruta).json()
        
        if json_data.get("code") == "Ok":
            ruta = json_data["routes"][0]
            
            # RELLENADO: OSRM entrega la distancia en metros, dividimos en 1000 para Kilómetros
            distancia_km = ruta["distance"] / 1000
            
            # RELLENADO: OSRM entrega la duración en segundos totales, pasamos a minutos dividiendo por 60
            duracion_min = ruta["duration"] / 60
            
            # Simulación de combustible (Consumo promedio: 0.08 lts por km)
            fuel_used = distancia_km * 0.08
            
            print("\n=============================================")
            print(f"Directions from: {coords_orig[2]}")
            print(f"To: {coords_dest[2]}")
            print(f"Trip Duration: {int(duracion_min // 60)}h {int(duracion_min % 60)}min")
            print(f"Kilometers: {distancia_km:.2f} km")
            print(f"Fuel Used (Ltr): {fuel_used:.2f}")
            print("=============================================")
            
            # 3. Imprimir maniobras (instrucciones) con manejo de errores
            print("Instrucciones de viaje:")
            for leg in ruta["legs"]:
                for step in leg["steps"]:
                    maneuver = step.get("maneuver", {})
                    # Intentamos obtener 'instruction'
                    maniobra = maneuver.get("instruction")
                    if not maniobra:
                        m_type = maneuver.get("type", "proceder")
                        m_mod = maneuver.get("modifier", "")
                        maniobra = f"{m_type} {m_mod}".strip().capitalize()
                    dist_step = step.get("distance", 0) / 1000
                    print(f" • {maniobra} ({dist_step:.2f} km)")
            print("=============================================\n")
        else:
            status = json_data.get("code")
            print(f"**********************************************")
            print(f"Status Code: {status}; No se pudo calcular la ruta.")
            print(f"**********************************************\n")
            
    except Exception as e:
        print(f"**********************************************")
        print(f"Error de red o parseo JSON en el servidor: {e}")
        print(f"**********************************************\n")