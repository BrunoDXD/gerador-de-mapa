import folium
import re
from geopy.geocoders import Nominatim
import time
from folium import plugins

# Dados brutos fornecidos pelo usuário
# Ler dados do arquivo temporário
with open("C:\Users\Bruno\Desktop\Scripts\dados_temp.txt", "r", encoding="utf-8") as f:
    dados_brutos = f.read()

# Dados brutos originais
"""
Latitude -23,40 Longitude -46,32 Arujá (+5 km), Atibaia (+20 km), Latitude -23,50 Longitude -46,85 Barueri (+3 km), Bragança Paulista (+20 km), Campinas (+20 km), Latitude -23,47 Longitude -46,53 Guarulhos (+5 km), Latitude -23,82 Longitude -45,37 Ilhabela (+20 km), Indaiatuba (+20 km), Itatiba (+20 km), Itu (+20 km), Jacareí (+20 km), Jundiaí (+20 km), Latitude -23,52 Longitude -46,19 Mogi das Cruzes (+5 km), Latitude -23,53 Longitude -46,79 Osasco (+5 km), Latitude -23,46 Longitude -46,83 Santana de Parnaíba (+3 km), Latitude -23,45 Longitude -46,92 Santana de Parnaíba (+5 km), Santos (+20 km), Latitude -23,71 Longitude -46,55 São Bernardo do Campo (+5 km), Latitude -23,62 Longitude -46,57 São Caetano do Sul (+5 km), São José dos Campos (+20 km), Latitude -23,53 Longitude -46,71 São Paulo (+3 km), Latitude -23,50 Longitude -46,63 São Paulo (+3 km), Latitude -23,45 Longitude -46,60 São Paulo (+3 km), Latitude -23,59 Longitude -46,68 São Paulo (+3 km), Latitude -23,56 Longitude -46,60 São Paulo (+3 km), Latitude -23,57 Longitude -46,73 São Paulo (+3 km), Latitude -23,58 Longitude -46,68 São Paulo (+3 km), Latitude -23,57 Longitude -46,55 São Paulo (+3 km), Latitude -23,56 Longitude -46,69 São Paulo (+3 km), Latitude -23,60 Longitude -46,72 São Paulo (+3 km), Latitude -23,63 Longitude -46,67 São Paulo (+3 km), Latitude -23,62 Longitude -46,69 São Paulo (+3 km), Latitude -23,60 Longitude -46,66 São Paulo (+3 km), Latitude -23,56 Longitude -46,69 São Paulo (+3 km), Latitude -23,56 Longitude -46,56 São Paulo (+3 km), Sorocaba (+20 km), Latitude -23,54 Longitude -46,31 Suzano (+5 km) São Paulo (state)
"""

# Substitui vírgulas decimais por pontos para conversão correta
dados_brutos = dados_brutos.replace(',', '.')

# Inicializa o geocodificador
geolocator = Nominatim(user_agent="mapa_com_raios")

# Expressão regular para extrair latitude, longitude, nome e raio
padrao_coordenadas = re.compile(
    r"Latitude\s*(-?\d+\.\d+)\s*Longitude\s*(-?\d+\.\d+)\s*([^\(]+)\(\+(\d+)\s*km\)",
    re.IGNORECASE
)

# Expressão regular para extrair apenas nome da cidade e raio (sem coordenadas)
padrao_cidade = re.compile(r"([^,\(]+)\(\+(\d+)\s*km\)", re.IGNORECASE)

# Lista de locais extraídos
locais = []

# Processa locais com coordenadas explícitas
for match in padrao_coordenadas.finditer(dados_brutos):
    lat = float(match.group(1))
    lon = float(match.group(2))
    nome = match.group(3).strip()
    raio_km = int(match.group(4))
    locais.append({"latitude": lat, "longitude": lon, "nome": nome, "raio_km": raio_km})

# Processa locais sem coordenadas explícitas
for match in padrao_cidade.finditer(dados_brutos):
    nome_cidade = match.group(1).strip()
    raio_km = int(match.group(2))
    
    # Verifica se esta cidade já foi processada pelo padrão anterior
    ja_processada = False
    for local in locais:
        if nome_cidade in local["nome"]:
            ja_processada = True
            break
    
    if not ja_processada:
        try:
            # Adiciona ", Brasil" para melhorar a precisão da geocodificação
            query = f"{nome_cidade}, São Paulo, Brasil"
            location = geolocator.geocode(query)
            
            if location:
                locais.append({
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "nome": nome_cidade,
                    "raio_km": raio_km
                })
                print(f"Geocodificado: {nome_cidade} -> ({location.latitude}, {location.longitude})")
                # Pausa para evitar limitações de taxa da API
                time.sleep(1)
            else:
                print(f"Não foi possível encontrar coordenadas para: {nome_cidade}")
        except Exception as e:
            print(f"Erro ao geocodificar {nome_cidade}: {e}")
            time.sleep(1)

# Cria o mapa centralizado no estado de SP
mapa = folium.Map(location=[-23.5, -46.6], zoom_start=8)

# Adiciona controle de tela cheia para facilitar uso em dispositivos móveis
plugins.Fullscreen(position='topright', title='Tela cheia', title_cancel='Sair da tela cheia').add_to(mapa)

# Adiciona controle de localização para dispositivos móveis
plugins.LocateControl(auto_start=False, strings={'title': 'Mostrar minha localização'}).add_to(mapa)

# Adiciona marcadores e círculos
for local in locais:
    folium.Marker(
        location=[local["latitude"], local["longitude"]],
        popup=f"{local['nome']} (+{local['raio_km']} km)",
        tooltip=local["nome"]
    ).add_to(mapa)

    folium.Circle(
        location=[local["latitude"], local["longitude"]],
        radius=local["raio_km"] * 1000,  # km para metros
        color='blue',
        fill=True,
        fill_opacity=0.2
    ).add_to(mapa)

# Salva o mapa como HTML
mapa.save("mapa_com_raios.html")

# Adicionar meta viewport para compatibilidade móvel
with open("mapa_com_raios.html", "r", encoding="utf-8") as file:
    content = file.read()

# Adicionar meta viewport para dispositivos móveis
content = content.replace(
    '<meta http-equiv="content-type" content="text/html; charset=UTF-8" />',
    '<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">'
)

# Adicionar estilos para garantir que o mapa ocupe toda a tela
content = content.replace(
    '<style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>',
    '<style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;} #map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>'
)

with open("mapa_com_raios.html", "w", encoding="utf-8") as file:
    file.write(content)

print(f"Mapa gerado com {len(locais)} locais e salvo como 'mapa_com_raios.html'.")

