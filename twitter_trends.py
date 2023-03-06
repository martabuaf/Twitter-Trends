## Librerias

import numpy as np
import pandas as pd

import requests

import tweepy
import twitter

import json
from pprint import pprint

import datetime
from time import sleep

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import folium

## Credenciales

# Credenciales Twitter

TWITTER_API_KEY = ""
TWITTER_API_KEY_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_BEARER_TOKEN = ""

# Credenciales Airtable

AIRTABLE_API_KEY = "" 
AIRTABLE_BASE_ID = "" 
AIRTABLE_TABLE_ID_TWT = "" 
AIRTABLE_TABLE_ID_WC = "" 

## Extracción de datos de Twitter y carga a Airtable

def load_data():
    
                                 ### Top 10 tendencias mundiales por país ###
    
    # Autentificación en la API de Twitter
    
    auth = tweepy.OAuthHandler(twitter_key, twitter_key_secret)
    
    auth.set_access_token(twitter_token, twitter_token_secret)

    api = tweepy.API(auth)
    
    # Cargamos los codigos WOE de los Paises

    codigos_woe = api.available_trends()

    df_woe = pd.DataFrame()

    df_woe["Lugar"] =  [result["name"] for result in codigos_woe]
    df_woe["Tipo"] = [result["placeType"]["name"] for result in codigos_woe]
    df_woe["Codigo"] = [result["woeid"] for result in codigos_woe]

    df_country = df_woe[df_woe["Tipo"].isin(["Country"])]    

    codigos_paises = pd.Series(df_country.Codigo.values,index=df_country.Lugar).to_dict() 
        
    # Llamada al API de Twitter para sacar los datos

    data = {"records" : list()}

    for pais, codigo in codigos_paises.items():

        top_trends = api.get_place_trends(codigo) # Tendencias de las últimas 24h por país

        for trend in top_trends[0]['trends']:

            data["records"].append({"fields" : {"Name"   : trend['name'],
                                                "Country": pais, 
                                                "Date"   : datetime.datetime.now().strftime("%y/%m/%d, %H:%M:%S"),
                                                "Url"    : trend['url'],
                                                "query"  : trend['query'],
                                                "Tweets Volume" : 0 if pd.isna(trend['tweet_volume']) else trend['tweet_volume']}})
    
    # Llamada al API de Airtable para cargar los datos

    airtable_base_url = "https://api.airtable.com/v0"

    endpoint = f"{airtable_base_url}/{airtable_base}/{airtable_twt}"

    headers = {"Authorization" : f"Bearer {airtable_key}",
               "Content-Type"  : "application/json"}

    params = {"fields"         : None, 
              "maxRecords"     : None, 
              "pageSize"       : None}

    for i in range(0, len(data["records"]), 10):

        datos_bucle = data["records"][i : i + 10]

        datos_carga = {"records" : datos_bucle}

        response = requests.post(url = endpoint, json = datos_carga, headers = headers)

        sleep(1)
        
                                 ### Evolución tendencias del Mundial ###
        
    if datetime.datetime.now().strftime("%A")=='Monday': # Saco datos únicamente los LUNES

        world_cup_official_hashtags = ["#FIFAWorldCup", "#Qatar2022"]

        # Llamada al API de Twitter para sacar los datos

        api = tweepy.Client(twitter_bearer)

        data = {"records" : list()}


        for query in world_cup_official_hashtags:

            counts = api.get_recent_tweets_count(query = query, granularity='hour') # Volumen de tweets de los últimos 7 días

            for count in counts[0]:

                data["records"].append({"fields" : {"trend" : query,
                                                    "start" : count["start"], 
                                                    "end"   : count["end"],
                                                    "count" : count["tweet_count"]}})

        # Llamada al API de Airtable para cargar los datos

        airtable_base_url = "https://api.airtable.com/v0"

        endpoint = f"{airtable_base_url}/{airtable_base}/{airtable_wc}"

        headers = {"Authorization" : f"Bearer {airtable_key}",
                   "Content-Type"  : "application/json"}

        params = {"fields"                : None, 
                  "maxRecords"            : None, 
                  "pageSize"              : None,}

        for i in range(0, len(data["records"]), 10):

            datos_bucle = data["records"][i : i + 10]

            datos_carga = {"records" : datos_bucle}

            response = requests.post(url = endpoint, json = datos_carga, headers = headers)

            sleep(1)
            
    return print("Finalizado el proceso de carga")
    
load_data()

## Extracción de datos de Airtable y transformación a DataFrame

def get_data_top10(formula = None):
    
    # Llamada al API de Airtable para extraer los datos

    airtable_base_url = "https://api.airtable.com/v0"

    endpoint = f"{airtable_base_url}/{airtable_base}/{airtable_twt}"

    headers = {"Authorization" : f"Bearer {airtable_key}",
               "Content-Type"  : "application/json"}

    # Primera página
    
    stop = False

    params = {"offset" : None, "filterByFormula" : formula}

    response = requests.get(url = endpoint, headers = headers, params = params)

    data = response.json()
    
    try:
        offset = data["offset"]
        
    except:
        stop=True

    nombres = [record["fields"]["Name"] for record in data["records"]]
    paises = [record["fields"]["Country"] for record in data["records"]]
    fechas = [record["fields"]["Date"] for record in data["records"]]
    urls = [record["fields"]["Url"] for record in data["records"]]
    consultas = [record["fields"]["query"] for record in data["records"]]
    volumenes = [record["fields"]["Tweets Volume"] for record in data["records"]]
    
    # Siguientes páginas

    while stop == False:
        
        params = {"offset" : offset, "filterByFormula" : formula}             
        
        response = requests.get(url = endpoint, headers = headers, params = params)

        data = response.json()

        nombres.extend([record["fields"]["Name"] for record in data["records"]])
        paises.extend([record["fields"]["Country"] for record in data["records"]])
        fechas.extend([record["fields"]["Date"] for record in data["records"]])
        urls.extend([record["fields"]["Url"] for record in data["records"]])
        consultas.extend([record["fields"]["query"] for record in data["records"]])
        volumenes.extend([record["fields"]["Tweets Volume"] for record in data["records"]])

        try:
            offset = data["offset"]

        except:
            stop = True

    # Creo el DataFrame

    df_twt = pd.DataFrame()

    df_twt["Nombre"] = nombres
    df_twt["Pais"] = paises
    df_twt["Fecha"] = fechas
    df_twt["Url"] = urls
    df_twt["Consulta"] = consultas
    df_twt["Volumen de tweets"] = volumenes

    #df_twt.to_csv(f'Twitter_trends_{datetime.datetime.now().strftime("%Y%m%d")}.csv', header=False, index=False)
    
    return df_twt

def get_data_wc():
    
    # Llamada al API de Airtable para extraer los datos

    airtable_base_url = "https://api.airtable.com/v0"

    endpoint = f"{airtable_base_url}/{airtable_base}/{airtable_wc}"

    headers = {"Authorization" : f"Bearer {airtable_key}",
               "Content-Type"  : "application/json"}

    # Primera página
    
    stop = False

    params = {"offset" : None}

    response = requests.get(url = endpoint, headers = headers, params = params)

    data = response.json()

    trends = [record["fields"]["trend"] for record in data["records"]]
    starts = [record["fields"]["start"] for record in data["records"]]
    ends = [record["fields"]["end"] for record in data["records"]]
    counts = [record["fields"]["count"] for record in data["records"]]
    
    try:
        offset = data["offset"]

    except:
        stop = True  

    # Siguientes páginas

    while stop == False:

        params = {"offset" : offset}

        response = requests.get(url = endpoint, headers = headers, params = params)

        data = response.json()

        trends.extend([record["fields"]["trend"] for record in data["records"]])
        starts.extend([record["fields"]["start"] for record in data["records"]])
        ends.extend([record["fields"]["end"] for record in data["records"]])
        counts.extend([record["fields"]["count"] for record in data["records"]])

        try:
            offset = data["offset"]

        except:
            stop = True


    # Creo el DataFrame

    df_wc = pd.DataFrame()

    df_wc["trend"] = trends
    df_wc["start"] = starts
    df_wc["end"] = ends
    df_wc["count"] = counts

    df_wc.sort_values("start", inplace = True)

    #df_wc.to_csv(f'World_Cup_trends_{datetime.datetime.now().strftime("%Y%m%d")}.csv', header=False, index=False)
    
    return df_wc
    
## Visualizaciones

def top_10(): # Mapa de las 10 tendencias con mayor volumen de tweets por país
    
    # Obtengo el DataFrame

    df_twt = get_data_top10(formula = "{Tweets Volume}>100000")  
    
    # Limpio los datos

    countries_dict = {"Korea" : "Republic of Korea", "Russia" : "Russian Federation", "United States" : "United States of America"}

    df_twt.replace(countries_dict, inplace = True)

    # Añado las coordenadas de cada pais al DataFrame

    centroides = json.load(open("un-country-centroids.json"))

    centroides.append({'name': 'Puerto Rico', 'lat': 18.242540, 'long': -66.490664}) # Añado las coordenadas que faltan

    df_coord = pd.DataFrame()

    df_coord["Pais"] = [cen["name"] for cen in centroides]
    df_coord["Latitud"] = [cen["lat"] for cen in centroides]
    df_coord["Longitud"] = [cen["long"] for cen in centroides]

    df_twt = pd.merge(df_twt, df_coord, on = "Pais", how = "left")

    # Creamos el mapa

    mapa_twt = folium.Map(location = [27, 30], zoom_start = 2, tiles = "CartoDB Positron")

    for pais in df_twt["Pais"].unique():

        df_top_trends_country = pd.DataFrame(df_twt[df_twt["Pais"] == pais].groupby("Nombre", as_index = False).first()).sort_values("Volumen de tweets", ascending = False).head(10)

        coord = (df_top_trends_country.iloc[0]["Latitud"],df_top_trends_country.iloc[0]["Longitud"])
        trends = df_top_trends_country["Nombre"].values
        vols = df_top_trends_country["Volumen de tweets"].values

        # Definimos el html

        html_header = f"""<h3 style="font-family:Verdana;font-size:14px;color:#4682B4;text-align: center;">Top 10 trends in {pais}</h3><div style="text-align: center;"><table style="margin:auto;font-family:Verdana;font-size:12px;color:#4682B4;">"""

        html_body = str()

        for i in range(10):
            html_body += f"""<tr style="border-bottom: 1px solid #ddd;"><td><strong>#{i+1}</strong></td><td>{trends[i]}</td><td>{round((vols[i]/1000_000), 2)}M</td></tr>"""

        html_tail = f"""</table></div><p style="font-family:Verdana;font-size:8px;color:#808080;">Data provided by ©2022 TWITTER INC.</p>"""

        html = html_header + html_body + html_tail

        icon = folium.features.CustomIcon("twitter_icon.png", icon_size=(40,40))

        iframe = folium.IFrame(html = html, width = 200, height = 250)

        popup = folium.Popup(iframe, width=200, height = 250)

        folium.Marker(location = coord, icon=icon, popup = popup, tooltip = pais).add_to(mapa_twt)
        
        mapa_twt.save("twt_top_trends.html")

    return mapa_twt
    
def top_trends(): # Gráfico de las 30 tendencias más usadas
    
    # Obtengo el DataFrame

    df_twt = get_data_top10(formula = "{Tweets Volume}>0")  
    
    # Limpio los datos
    
    counts = dict()
    
    words = df_twt.Nombre

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    df_words = pd.DataFrame(counts.items(), columns=['words', 'count'])

    df_words.sort_values("count", ascending = False, inplace = True)

    # Colores

    colors = plt.cm.get_cmap(name = "Blues", lut = 30)

    cmap = [colors(i) for i in np.linspace(0, 1, 30)]
    
    # Creo el gráfico

    fig, ax = plt.subplots(figsize=(12,12), facecolor='white')

    labels = list(df_words['words'][0:30])

    counts = list(df_words['count'][0:30])

    labels.reverse()

    counts.reverse()

    # Añado los círculos

    circles = circlify.circlify(df_words['count'][0:30].tolist(), show_enclosure=False, target_enclosure=circlify.Circle(x=0, y=0))

    for circle, label, count, color in zip(circles, labels, counts, cmap):

        x, y, r = circle

        ax.add_patch(plt.Circle(xy = (x, y), radius = r, alpha = 0.8, color = color))

        plt.annotate(text = (f"{label}\n{count} veces"), xy = (x, y), size = 12, va = 'center', ha = 'center')
    
    lim = max(max(abs(circle.x)+circle.r, abs(circle.y)+circle.r,) for circle in circles)

    plt.xlim(-lim, lim)

    plt.ylim(-lim, lim)
    
    fontdict = {'fontsize': 24, 'color': "black", 'verticalalignment': 'baseline'}
    
    ax.set_title(label = "Tendencias más usadas en Twitter", fontdict = fontdict, loc=None, pad=None, y= 0.95)
    
    ax.axis('off')
    
    plt.savefig("twt_top_circles.png")
    
    return plt.show()
    
def world_cup_frec(): # Mapa de frecuencia de los hashtags del Mundial 2022 por país
    
    # Obtengo el DataFrame
    
    df_twt = get_data_top10(formula = "OR({Name}='#FIFAWorldCup',{Name}='#Qatar2022')")
    
    world_geo = "paises_twitter.json"

    world_cup_official_hashtags = ["#FIFAWorldCup", "#Qatar2022"]

    df_cor = pd.DataFrame(df_twt[df_twt["Nombre"].isin(world_cup_official_hashtags)])

    # Obtengo la frecuencia de las tendencias en cada país
    
    paises = df_cor["Pais"].unique()

    dic={}

    for i in paises:    

        dic[i] = len(df_cor[df_cor["Pais"]==i]["Fecha"].unique())

    df_mapa = pd.DataFrame(dic.items(), columns = ["Pais", "Frecuencia"])

    countries_dict = {"Korea" : "Republic of Korea", "Russia" : "Russian Federation", "United States" : "United States of America"}

    df_mapa.replace(countries_dict, inplace = True)

    # Creo el mapa

    world_map = folium.Map(location = [28, 0], zoom_start = 2)

    folium.Choropleth(geo_data = world_geo, data = df_mapa, columns = ["Pais", "Frecuencia"], key_on = "feature.properties.name", legend_name = "Frecuencia de las tendencias del Mundial", nan_fill_color = "lightgrey", fill_color = "Blues", line_color = "grey", highlight = True).add_to(world_map)
    
    world_map.save("twt_count_trends.html")

    return world_map
    
def world_cup_evol(): # Gráfico de lineas de evolución de los hastags del Mundial 2022
    
    # Obtengo el DataFrame
    
    df_wc = get_data_wc()

    # Creamos el gráfico

    fig = go.Figure()

    fig.add_trace(go.Scatter(x = df_wc.groupby("start", as_index = False).agg("sum")["start"], y = df_wc.groupby("start", as_index = False).agg("sum")["count"], name = "Volumen total", line = dict(color = "steelblue")))

    fig.add_trace(go.Scatter(x = df_wc[df_wc["trend"] == "#FIFAWorldCup"]["start"], y = df_wc[df_wc["trend"] == "#FIFAWorldCup"]["count"], name = "#FIFAWorldCup", line = dict(color = "cornflowerblue")))

    fig.add_trace(go.Scatter(x = df_wc[df_wc["trend"] == "#Qatar2022"]["start"], y = df_wc[df_wc["trend"] == "#Qatar2022"]["count"], name = "#Qatar2022", line = dict(color = "lightsteelblue")))

    fig.update_xaxes(rangeslider_visible = True)

    fig.update_layout(legend_title_text = "Tendencias")
    
    fig.write_html("twt_wc_evol.html")

    return fig
    
## Ejecución del código: Como hemos utilizado funciones anidadas sólo es necesario ejecutar cada una de las visualizaciones

#top_10()

#top_trends()

#world_cup_frec()

#world_cup_evol()
