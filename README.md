# MegaDD-Crawler

Crawler para Megadede, pero solo para la sección de series. Recorre todas las series disponibles y almacena en MongoDB la información obtenida.

Lo que se extrae es:
  -Titulo
  -Temporadas
    -Nombre de la temporada
    -Número de temporada
  -Capítulos
    -Lenguaje
    -Calidad
    -Uploader
    -Servidor
    -Enlace externo

El crawler almacena la información en una base de datos MongoDB con tres tablas, una para series, otra para capitulos y una última para los enlaces externos de los capitulos.

Para ejecutar el proyecto es necesario estar autenticado en la página, por lo que se necesita la POST Request de inicio de sesión. Una vez obtenida, hay que transformar el comando cURL (por ejemplo en [curl.trillworks.com](curl.trillworks.com)) a una request de python y el resultado de eso introducirlo en el archivo  [series_spider](https://github.com/eduardez/MegaDD-Crawler/blob/master/spiders/series_spider.py).


Todo esto viene de que me estaba viendo The Boys pero justo sacaron el comunicado de que cerraban.
