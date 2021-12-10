# Easycrypto

Python para el análisis de datos – Proyecto Final

Introducción
Me gustaría hacer un breve inciso antes de entrar en los detalles del proyecto. Debido al poco tiempo que hemos tenido disponible para llevar a cabo el proyecto y de mi escasa 
experiencia en programación más allá de hacer pequeños scripts, muchas de las decisiones tomadas en el desarrollo de este proyecto están basadas en conseguir terminar y entregar 
un proyecto funcional a tiempo. Esto implica que en varias ocasiones no he optado por la mejor solución, sino por la más sencilla para hacer que funcione.

Alcance del proyecto
El proyecto se compone de un dashboard en Streamlit de cotizaciones de criptomonedas que extrae los datos de la API de Kraken. En dicho dashboard representamos en una misma 
gráfica la información OHLC en velas, el VWAP y el volumen de las transacciones. Tenemos dos selectores laterales que nos permiten escoger el par a visualizar (BTC-USD y ETH-USD)
y el intervalo de las velas. 
El proyecto está alojado en la nube gratuita de Streamlit, y puede verse en el siguiente enlace. Adicionalmente, el proyecto está subido a GitHub y puede verse aquí.
La principal limitación del proyecto es que el límite de la antigüedad de los datos depende del intervalo elegido de las velas. Esto se debe a que el proyecto se ha realizado
sobre la llamada a la API “OHLC”, que devuelve la información OHLC de los 720 registros más recientes (hay un parámetro “Since” en la API, pero sólo sirve para limitar la
respuesta dentro de estos 720 registros). La solución a esto pasaría por hacer una llamada diferente a la API bajando los trades (ClosedOrders), que no tienen dicho límite, y
calcular yo mismo los OHLC de los distintos periodos. Lamentablemente cuando fui consciente de este problema ya era muy tarde para poder hacerlo y conseguir hacer la entrega a
tiempo.


Estructura
El proyecto está estructurado con Poetry y contiene un archivo pyproject.toml donde se encuentran todas las dependencias del mismo. El código a ejecutar se encuentra en la
carpeta easycrypto y se llama app.py.

El código está compuesto por 4 bloques principales y diferenciados: 
•	Un primer bloque genera un dataset de pandas en base a los datos recibidos de la API de Kraken. 
•	Un segundo bloque, donde tenemos una función para calcular en VWAP que aplicamos al dataset.
•	Un tercer bloque, donde generamos los elementos de streamlit.
•	Un cuarto y último bloque, donde se generan las gráficas que se verán en el dashboard.
Por último, mencionar que el código está extensamente comentado para que sea lo más fácil posible de entender.
