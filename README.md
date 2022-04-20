# epiweb2godata

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">Exportación de Epiweb a Go.Data</h3>

  <p align="center">
    Transformación del reporte de COVID-19 de Epiweb para la exportación a Go.Data.
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Índice</summary>
  <ol>
    <li>
      <a href="#sobre-el-proyecto">Sobre el proyecto</a>
      <ul>
        <li><a href="#desarrollado-con">Desarrollado con</a></li>
      </ul>
    </li>
    <li>
      <a href="#para-empezar">Para empezar</a>
      <ul>
        <li><a href="#prerequisitos">Prerequisitos</a></li>
        <li><a href="#instalacion">Instalación</a></li>
      </ul>
    </li>
    <li><a href="#uso">Uso</a></li>
    <li><a href="#contacto">Contacto</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## Sobre el proyecto

En Go.Data se realiza el seguimiento de casos y contactos COVID-19 en Guatemala. Pero las fichas epidemiológicas que captan a los casos COVID-19 son almacenados en el sistema de EPIWEB. Este proyecto con epiweb2godata.py busca automatizar el proceso de transformación y carga de la base de datos de EPIWEB a Go.Data.

### Desarrollado con

* [Python 3](https://www.python.org/downloads/)
* [Pandas](https://pandas.pydata.org/)
* [Numpy](https://numpy.org/)

<!-- GETTING STARTED -->
## Para empezar


### Prerequisitos

* Python
  ```sh
  sudo apt-get install python3
  sudo apt-get install python3-pip
  pip3 install pandas
  pip3 install numpy
  pip3 install datetime
  pip3 install requests
  ```

### Instalación

1. Clonar el repositorio
   ```sh
   git clone https://github.com/Oliversinn/epiweb2godata.git
   ```

<!-- USAGE EXAMPLES -->
## Uso

1. Funcionalidades generales
  ```sh
   epiweb2godata.py [-h] [--csv CSV] [--brote BROTE] [--ignorar IGNORAR]
                        --usuario USUARIO --contraseña CONTRASEÑA

  -h, --help            Muestra este mensaje de ayuda.
  --csv CSV, -csv CSV   Nombre del archivo csv.
  --brote BROTE, -b BROTE
                        Seleccionar brote al que se subiran los datos.
                        (rastreo, capacitaciones, pruebas)
  --ignorar IGNORAR, -i IGNORAR
                        Cantidad de casos a ignorar al momento de subir los
                        datos.
  --usuario USUARIO, -u USUARIO
                        Usuario de Go.Data
  --contraseña CONTRASEÑA, -c CONTRASEÑA
                        Contraseña de Go.Data
  ```
2. Subir base de datos
    La base de datos debe estar en la misma carpeta que el programa, debe tener el nombre de casos_epiweb.csv y el csv estar separado por "|".
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña
  ```

3. Subir base de datos al ambiente de pruebas
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña -b pruebas
  ```
4. Subir base de datos al ambiente de capacitaciones
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña -b capacitaciones
  ```
5. Subir base de datos al ambiente de pruebas
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña -b pruebas
  ```
6. Subir base de datos ignorando los primeros 100 datos
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña -i 100
  ```
6. Subir base de datos con nombre dstinto a casos_epiweb.csv
  ```sh
  python3 epiweb2godata.py -u usuario@godata.com -c micontraseña -csv nombredistinto.csv
  ```
<!-- CONTACT -->
## Contacto

[Oliver Mazariegos](https://mazariegos.gt/) - oliver@mazariegos.gt

Repo Link: [https://github.com/Oliversinn/epiweb2godata](https://github.com/Oliversinn/epiweb2godata)

