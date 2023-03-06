<h1> Twitter : Tendencias mundiales</h1>
<p>En este proyecto vamos a analizar y visualizar las tendencias mundiales en la red social Twitter. 
Estas tendencias aparecen en la categoría "What's happening". Para ello crearemos una ETL (Extracción, Transformación, Carga) que haga una llamada a la api de Twitter y cargue los datos a una base de datos local en AirTable. 
<p>
Aprovecharemos la actual actividad en Twitter sobre el Mundial de fútbol para hacer un análisis más detallado sobre la cantidad de tweets sobre el Mundial por cada país y su evolución temporal.
</p>

### Paso 1: Acceso a la API
Acceder a la API Twitter y obtener los credenciales para hacer las consultas. Es necesario extender el nivel de autorizacion de Esential a Elevated para obtener los permisos necesarios para llevar a cabo este proyecto.

Utilizaremos Tweepy para interactuar con la api. Tweepy ofrece una interfaz más sencilla y fácil de utilizar. 

La documentación de Tweepy la encontramos aquí: https://docs.tweepy.org/en/stable/api.html

### Paso 2: Parámetros de la API
Las busquedas de tendencias por lugar de Twitter se hacen a tarvés del código WOE del país o ciudad. Para poder buscar por el codigo de los paises necesitamos un diccionario con el nombre de cada pais y su correspondiente código WOE.

Encontramos el archivo con los codigos WOE aquí: https://codebeautify.org/jsonviewer/f83352

### Paso 3: Estracción y transformación de datos
Extraer la información relevante sobre los top_trend de cada pais en tiempo real y transformar los datos a un json que tenga la estructura deseada para hacer la carga a una base de datos.

### Paso 4: Carga de datos
Almacenar esta información en una base de datos local como AirTable. El nombre de las columnas es el mismo que en la base de datos, nos aseguramos de que el tipo de datos en cada columna sea el correcto para que la carga se lleve acabo satisfactoriamente.
<table>
    <tr>
        <td>Nombre</td>
        <td>str</td>
    </tr>
    <tr>
        <td>Pais</td>
        <td>str</td>
    </tr>
    <tr>
        <td>Fecha</td>
        <td>str</td>![World_Cup_hashtags](https://user-images.githubusercontent.com/122131317/223225946-34023102-1bc5-47c0-8d8d-b231dc2af965.png)

    </tr>
    <tr>
        <td>Url</td>
        <td>url</td>
    </tr>
    <tr>
        <td>Consulta</td>
        <td>str</td>
    </tr>
    <tr>
        <td>Volumen de tweets</td>
        <td>float (no almacena Nan)</td>
    </tr>
</table>

### Paso 5: Extracción y transformación de datos
Extraer los datos totales de AirTable y transformarlos a un DataFrame para que sean más accesibles.

### Paso 6: Visualizaciones
Visualizar la información en un mapa folium que represente a modo de pop-up el Top 10 de tendencias en cada país.

### Paso 7: Ampliación
Analizar la actividad en Twitter sobre el Mundial. Para ello tomamos como valores a medir la cantidad y frecuencia con la que se usan los hashtags oficiales en cada país en un mapa Choropleth. Y una línea de evolución temporal de la actividad en gráficos Plotly. 
<p align="center">
<img src = "https://user-images.githubusercontent.com/122131317/223226155-c3ae4df8-217e-43aa-b35e-269998c3dcd0.png" width="350"/>
</p>

<p>Nota: Los hashtags estan disponibles desde el 17 de noviembre hasta el 31 de Diciembre de 2022.</p>
