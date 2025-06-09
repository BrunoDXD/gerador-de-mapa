import folium
import re
from geopy.geocoders import Nominatim
import time
from folium import plugins

# Dados brutos fornecidos
# Ler dados do arquivo temporário
with open("C:\Users\Bruno\Desktop\Scripts\dados_temp.txt", "r", encoding="utf-8") as f:
    raw_data = f.read()

# Dados brutos originais
"""
Latitude -23,40 Longitude -46,32 Arujá (+5 km), Atibaia (+20 km), Latitude -23,50 Longitude -46,85 Barueri (+3 km), Bragança Paulista (+20 km), Campinas (+20 km), Latitude -23,47 Longitude -46,53 Guarulhos (+5 km), Latitude -23,82 Longitude -45,37 Ilhabela (+20 km), Indaiatuba (+20 km), Itatiba (+20 km), Itu (+20 km), Jacareí (+20 km), Jundiaí (+20 km), Latitude -23,52 Longitude -46,19 Mogi das Cruzes (+5 km), Latitude -23,53 Longitude -46,79 Osasco (+5 km), Latitude -23,46 Longitude -46,83 Santana de Parnaíba (+3 km), Latitude -23,45 Longitude -46,92 Santana de Parnaíba (+5 km), Santos (+20 km), Latitude -23,71 Longitude -46,55 São Bernardo do Campo (+5 km), Latitude -23,62 Longitude -46,57 São Caetano do Sul (+5 km), São José dos Campos (+20 km), Latitude -23,53 Longitude -46,71 São Paulo (+3 km), Latitude -23,50 Longitude -46,63 São Paulo (+3 km), Latitude -23,45 Longitude -46,60 São Paulo (+3 km), Latitude -23,59 Longitude -46,68 São Paulo (+3 km), Latitude -23,56 Longitude -46,60 São Paulo (+3 km), Latitude -23,57 Longitude -46,73 São Paulo (+3 km), Latitude -23,58 Longitude -46,68 São Paulo (+3 km), Latitude -23,57 Longitude -46,55 São Paulo (+3 km), Latitude -23,56 Longitude -46,69 São Paulo (+3 km), Latitude -23,60 Longitude -46,72 São Paulo (+3 km), Latitude -23,63 Longitude -46,67 São Paulo (+3 km), Latitude -23,62 Longitude -46,69 São Paulo (+3 km), Latitude -23,60 Longitude -46,66 São Paulo (+3 km), Latitude -23,56 Longitude -46,69 São Paulo (+3 km), Latitude -23,56 Longitude -46,56 São Paulo (+3 km), Sorocaba (+20 km), Latitude -23,54 Longitude -46,31 Suzano (+5 km) São Paulo (state)
"""

# Substituir vírgulas decimais por pontos
raw_data = raw_data.replace(',', '.')

# Inicializa o geocodificador
geolocator = Nominatim(user_agent="mapa_sem_raio")

# Expressão regular para extrair coordenadas explícitas
pattern_coords = r"Latitude (-?\d+\.\d+)\s+Longitude (-?\d+\.\d+)\s+([^\(]+)\(\+(\d+) km\)"

# Expressão regular para extrair apenas nome da cidade e raio (sem coordenadas)
pattern_city = r"([^,\(]+)\(\+(\d+)\s*km\)"

# Lista para armazenar todos os locais
locations = []

# Extrair os dados com coordenadas explícitas
matches_coords = re.findall(pattern_coords, raw_data)

# Processar locais com coordenadas explícitas
for lat, lon, nome, raio in matches_coords:
    locations.append({
        "latitude": float(lat),
        "longitude": float(lon),
        "nome": nome.strip(),
        "raio": int(raio)
    })

# Extrair cidades sem coordenadas explícitas
matches_city = re.findall(pattern_city, raw_data)

# Processar cidades sem coordenadas explícitas
for nome_cidade, raio in matches_city:
    nome_cidade = nome_cidade.strip()
    
    # Verifica se esta cidade já foi processada pelo padrão anterior
    ja_processada = False
    for local in locations:
        if nome_cidade in local["nome"]:
            ja_processada = True
            break
    
    if not ja_processada:
        try:
            # Adiciona ", Brasil" para melhorar a precisão da geocodificação
            query = f"{nome_cidade}, São Paulo, Brasil"
            location = geolocator.geocode(query)
            
            if location:
                locations.append({
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "nome": nome_cidade,
                    "raio": int(raio)
                })
                print(f"Geocodificado: {nome_cidade} -> ({location.latitude}, {location.longitude})")
                # Pausa para evitar limitações de taxa da API
                time.sleep(1)
            else:
                print(f"Não foi possível encontrar coordenadas para: {nome_cidade}")
        except Exception as e:
            print(f"Erro ao geocodificar {nome_cidade}: {e}")
            time.sleep(1)

# Criar o mapa centralizado no estado de SP
mapa = folium.Map(location=[-23.5, -46.5], zoom_start=8)

# Adicionar marcadores personalizados
for local in locations:
    folium.Marker(
        location=[local["latitude"], local["longitude"]],
        popup=local["nome"],
        icon=folium.Icon(color='blue', icon='map-marker', prefix='fa')
    ).add_to(mapa)

# Adicionar controles de zoom para facilitar uso em dispositivos móveis
folium.plugins.Fullscreen().add_to(mapa)

# Adicionar cabeçalho HTML personalizado para melhorar compatibilidade móvel
html_header = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        html, body, #map {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
"""

# Salvar o mapa como HTML com cabeçalho personalizado
mapa.save("mapa_com_pinos_personalizados.html")

# Adicionar plugins necessários ao arquivo HTML
with open("mapa_com_pinos_personalizados.html", "r", encoding="utf-8") as file:
    content = file.read()

# Adicionar importação do plugin Fullscreen
content = content.replace(
    '<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>\n    <script src="https://cdn.jsdelivr.net/npm/leaflet-fullscreen@1.0.2/dist/Leaflet.fullscreen.min.js"></script>\n    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet-fullscreen@1.0.2/dist/leaflet.fullscreen.css"/>'
)

with open("mapa_com_pinos_personalizados.html", "w", encoding="utf-8") as file:
    file.write(content)

print(f"Mapa com pinos personalizados gerado com {len(locations)} locais e salvo como 'mapa_com_pinos_personalizados.html'.")

