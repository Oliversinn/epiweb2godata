library(readr)
library(dplyr)

# packages for this script
packages = c('readr','dplyr')
# check if packages are installed
package.check = lapply(
  packages,
  FUN = function(x) {
    if (! suppressMessages(require(x,character.only = TRUE))) {
      install.packages(x, dependencies = TRUE)
      suppressMessages(library(x, character.only = TRUE))
    }
  }
)

## ESCRIBIR ACA LA DIRECCION DE LA CARPETA epiweb2godata
setwd("~/Documents/MSPAS/epiweb2godata")

## INTRODUCIR CASOS QUE SE LOGRARON SUBIR
casos_subidos = 48

## LEER BASE DE DATOS
epiweb = read_delim('casos_epiweb.csv', guess_max = 50000, delim = '|')
epiweb = epiweb %>% 
  filter(
    distrito == 'JOCOTÁN' | 
      distrito == 'CHIQUIMULA' | 
      distrito == 'SAN SEBASTIÁN' | 
      distrito == 'SAN FELIPE',
    as.Date(fecha_notificacion, format = '%d/%m/%Y') > (Sys.Date() - 7)
  )

filtrados = epiweb[c(casos_subidos:nrow(epiweb)),]

write_delim(filtrados, 'casos_epiweb.csv', delim = '|')
