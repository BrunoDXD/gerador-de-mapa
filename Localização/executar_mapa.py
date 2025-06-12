import folium
import re
from folium import plugins

# Dados brutos fornecidos pelo usuário
dados_brutos = """
Cotia (06711), Latitude -23,40 Longitude -46,32 Arujá (+5 km), Atibaia (+20 km), Latitude -23,50 Longitude -46,85 Barueri (+3 km), Bragança Paulista (+20 km), Campinas (+20 km), Latitude -23,60 Longitude -46,92 Cotia (+5 km), Guarujá (+20 km), Latitude -23,47 Longitude -46,53 Guarulhos (+5 km), Ilhabela (+20 km), Indaiatuba (+20 km), Itu (+20 km), Jacareí (+20 km), Jundiaí (+20 km), Latitude -23,52 Longitude -46,19 Mogi das Cruzes (+5 km), Latitude -23,53 Longitude -46,79 Osasco (+5 km), Latitude -23,45 Longitude -46,93 Santana de Parnaíba (+5 km), Latitude -23,46 Longitude -46,83 Santana de Parnaíba (+3 km), Latitude -23,66 Longitude -46,54 Santo André (+5 km), Santos (+20 km), Latitude -23,72 Longitude -46,57 São Bernardo do Campo (+5 km), São José dos Campos (+20 km), Latitude -23,58 Longitude -46,68 São Paulo (+3 km), Latitude -23,56 Longitude -46,60 São Paulo (+3 km), Latitude -23,58 Longitude -46,68 São Paulo (+3 km), Latitude -23,45 Longitude -46,60 São Paulo (+3 km), Latitude -23,56 Longitude -46,56 São Paulo (+3 km), Latitude -23,64 Longitude -46,70 São Paulo (+3 km), Latitude -23,53 Longitude -46,71 São Paulo (+3 km), Latitude -23,61 Longitude -46,52 São Paulo (+5 km), Latitude -23,63 Longitude -46,67 São Paulo (+3 km), Latitude -23,60 Longitude -46,66 São Paulo (+3 km), Latitude -23,57 Longitude -46,73 São Paulo (+3 km), Latitude -23,54 Longitude -46,64 São Paulo (+3 km), Latitude -23,59 Longitude -46,63 São Paulo (+3 km), Latitude -23,50 Longitude -46,63 São Paulo (+3 km), Latitude -23,62 Longitude -46,69 São Paulo (+3 km), Latitude -23,60 Longitude -46,72 São Paulo (+3 km), Latitude -23,57 Longitude -46,55 São Paulo (+3 km), Sorocaba (+20 km), Latitude -23,55 Longitude -46,31 Suzano (+5 km), Ubatuba (+20 km) São Paulo (state)
"""

# Substitui vírgulas decimais por pontos para conversão correta
dados_brutos = dados_brutos.replace(',', '.')

# Coordenadas conhecidas para cidades sem coordenadas explícitas
coordenadas_conhecidas = {
    "atibaia": (-23.12, -46.55),
    "campinas": (-22.91, -47.06),
    "indaiatuba": (-23.09, -47.21),
    "jacareí": (-23.31, -45.97),
    "jundiaí": (-23.19, -46.88),
    "são josé dos campos": (-23.18, -45.88),
    "sorocaba": (-23.50, -47.45)
}

# Lista para armazenar os locais extraídos
locais = []
cidades_processadas = set()

# Expressão regular para extrair coordenadas, nome e raio
padrao_coordenadas = re.compile(r"Latitude\s+(-?\d+\.\d+)\s+Longitude\s+(-?\d+\.\d+)\s+([^(]+)\(\+(\d+)\s*km\)")

# Processa o texto para extrair locais com coordenadas explícitas
for match in padrao_coordenadas.finditer(dados_brutos):
    lat = float(match.group(1))
    lon = float(match.group(2))
    nome = match.group(3).strip()
    raio_km = int(match.group(4))
    
    locais.append({
        "latitude": lat,
        "longitude": lon,
        "nome": nome,
        "raio_km": raio_km
    })
    cidades_processadas.add(nome.lower())
    print(f"Coordenadas encontradas: {nome} -> ({lat}, {lon}) com raio de {raio_km} km")

# Expressão regular para extrair apenas nome e raio (sem coordenadas)
padrao_cidade = re.compile(r"(?<![a-zA-Z])([A-Z][a-zÀ-ú]+(?: d[a-z]+ [A-Z][a-zÀ-ú]+| d[a-z]+ [A-Z][a-zÀ-ú]+| [A-Z][a-zÀ-ú]+)*)\s*\(\+(\d+)\s*km\)")

# Processa o texto para extrair locais sem coordenadas explícitas
for match in padrao_cidade.finditer(dados_brutos):
    nome = match.group(1).strip()
    raio_km = int(match.group(2))
    
    # Verifica se esta cidade já foi processada
    if nome.lower() not in cidades_processadas:
        # Verifica se temos coordenadas conhecidas para esta cidade
        nome_lower = nome.lower()
        if nome_lower in coordenadas_conhecidas:
            lat, lon = coordenadas_conhecidas[nome_lower]
            locais.append({
                "latitude": lat,
                "longitude": lon,
                "nome": nome,
                "raio_km": raio_km
            })
            cidades_processadas.add(nome_lower)
            print(f"Usando coordenadas conhecidas: {nome} -> ({lat}, {lon}) com raio de {raio_km} km")
        else:
            print(f"Não foi possível encontrar coordenadas para: {nome}")

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

    # Escolha de cor baseada no tamanho do raio
    if local["raio_km"] <= 5:
        cor = 'green'
        opacidade = 0.15
    elif local["raio_km"] <= 10:
        cor = 'blue'
        opacidade = 0.12
    elif local["raio_km"] <= 16:
        cor = 'orange'
        opacidade = 0.1
    else:  # 17-20km
        cor = 'red'
        opacidade = 0.08
    
    folium.Circle(
        location=[local["latitude"], local["longitude"]],
        radius=local["raio_km"] * 1000,  # km para metros
        color=cor,
        weight=2,
        fill=True,
        fill_opacity=opacidade,
        popup=f"Raio: {local['raio_km']} km"
    ).add_to(mapa)

# Adiciona uma legenda ao mapa
legenda_html = '''
<div style="position: fixed; 
            bottom: 20px; right: 20px; 
            border: 1px solid grey; 
            z-index: 9999; 
            background-color: white;
            padding: 6px;
            opacity: 0.8;
            border-radius: 5px;
            font-size: 12px;">
    <div style="margin-bottom: 3px;"><b>Legenda - Raios</b></div>
    <div><span style="color: green; font-size: 16px;">●</span> Até 5 km</div>
    <div><span style="color: blue; font-size: 16px;">●</span> 6-10 km</div>
    <div><span style="color: orange; font-size: 16px;">●</span> 11-16 km</div>
    <div><span style="color: red; font-size: 16px;">●</span> 17-20 km</div>
</div>
'''

mapa.get_root().html.add_child(folium.Element(legenda_html))

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
print(f"Cidades incluídas: {', '.join(sorted([local['nome'] for local in locais]))}")