"""
Oliver Mazariegos - oliver@mazariegos.gt

Este script lee un archivo CSV exportado de EPIWEB, lo transforma y lo importa a Go.Data
"""


# Importacion de las librerias necesarias por correr el script.
import pandas as pd
import argparse
import numpy as np
import time
import requests
from datetime import date, timedelta
import sys
requests.packages.urllib3.disable_warnings() 

# Section of input arguments
par=argparse.ArgumentParser(description='Este archivo sube la base de datos de COVID-19 de EPIWEB a Go.Data.')
par.add_argument('--csv','-csv',dest='csv',type=str,help='Nombre del archivo csv.',required=False, default='casos_epiweb.csv')
par.add_argument('--brote','-b',dest='brote',type=str,help='Seleccionar brote al que se subiran los datos. (rastreo, capacitaciones, pruebas)',required=False, default='rastreo')
par.add_argument('--ignorar','-i',dest='ignorar',type=int,help='Cantidad de casos a ignorar al momento de subir los datos.',required=False, default=0)
par.add_argument('--usuario','-u',dest='usuario',type=str,help='Usuario de Go.Data',required=True)
par.add_argument('--contraseña','-c',dest='contraseña',type=str,help='Contraseña de Go.Data',required=True)
args=par.parse_args()

print('Iniciando script de transformación de casos de EPIWEB e importación a Go.Data\n', time.strftime('%d-%m-%y %H:%M'))

# Link del API de Go.Data
link = 'https://godataguatemala.mspas.gob.gt/api'
# Usuario de Go.Data
email= args.usuario
# Contraseña de Go.Data
password = args.contraseña

outbreaks = {
    'rastreo':'a44faf32-bf27-4b39-a4fb-b9fcf29ac2d7',
    'pruebas':'f1fb1ec0-3107-407a-8a14-c4c0bf927f8e',
    'capacitaciones':'7294fb63-7f71-46ee-bb65-856b1d983828'
}
outbreakId = outbreaks[args.brote]

# Lectura de datos
## Archivo exportado de EPIWEB
print('Leyendo archivo de EPIWEB')
epiweb = pd.read_csv(args.csv, sep='|', low_memory=False)
## Archivo con informacion de los IDs de las DMS en Go.Data
# print('Leyendo archivo con locationId de las DMS')
# dms = pd.read_csv('dms_godata_id.csv')
# ## Archivo con informacion de los IDs de las DAS en Go.Data
# print('Leyendo archivo con locationId de las DAS')
# das = pd.read_csv('das_godata_id.csv')
print('Leyendo archivo con locationID')
locationsId = pd.read_csv('locationsID.csv')
## Remover los casos que fueron contactos
#epiweb.drop(epiweb[epiweb.contacto_caso_confirmado == 'SI'].index, inplace=True)
#epiweb.drop(epiweb[epiweb.clasificacion == 'Descartado'].index, inplace=True)

## Remover los casos con fecha de notificación de hace 7 días o más

dias = date.today()-timedelta(7)
epiweb.drop(epiweb[pd.to_datetime(epiweb.fecha_notificacion, format= '%d/%m/%Y') <= pd.to_datetime(dias)].index, inplace=True)
#epiweb.to_csv('casos_epiweb.csv', sep='|', index = False)
areas = [
    "EL PROGRESO",
    "SACATEPÉQUEZ",
    "CHIMALTENANGO",
    "ESCUINTLA",
    "SANTA ROSA",
    "SOLOLÁ",
    "TOTONICAPÁN",
    "QUETZALTENANGO",
    "RETALHULEU",
    "SAN MARCOS",
    "HUEHUETENANGO",
    "QUICHÉ",
    "IXCÁN",
    "BAJA VERAPAZ",
    "ALTA VERAPAZ",
    "PETÉN NORTE",
    "PETÉN SUR OCCIDENTAL",
    "PETÉN SUR ORIENTAL",
    "IZABAL",
    "ZACAPA",
    "CHIQUIMULA",
    "JALAPA",
    "JUTIAPA",
    "IXIL",
    "GUATEMALA CENTRAL",
    "GUATEMALA NOR-OCCIDENTE",
    "GUATEMALA NOR-ORIENTE",
    "GUATEMALA SUR"
]
#
epiweb = epiweb[(epiweb['distrito'] == 'JOCOTÁN') | (epiweb['distrito'] == 'CHIQUIMULA') | (epiweb['distrito'] == 'SAN SEBASTIÁN') | (epiweb['distrito'] == 'SAN FELIPE') | (epiweb['area'] == 'PETÉN NORTE') | (epiweb['area'] == "GUATEMALA CENTRAL") | (epiweb['area'] == "QUETZALTENANGO") | (epiweb['area'] == "GUATEMALA NOR-ORIENTE") ]  
epiweb = epiweb[(epiweb['vigilancia'] != 'Descartado')]
# Seleccion de columnas a importar a Go.Data
columnas1 = ['nombres','apellidos','sexo','edad_anios','fecha_nacimiento','municipio','distrito',
           'direccion','departamento','telefono','area','servicio','fecha_notificacion','fecha_sintoma','embarazada',
           'clasificacion','condicion_egreso','ficha_registro','fecha_tomo_muestra','toma_muestra','tipo_muestra',
           'virus_detectados','cui','vigilancia','trabajador_salud','pueblo','ocupacion','escolaridad',
           'disnea','estridor','dolor_muscular','dolor_cabeza','mal_general','fiebre','odinofagia','rinorrea','tos',
           'disf_neuromuscular','diabetes','ant_fiebre','cardiopatia_cronica','obesidad','renal_cronica',
           'inmuno_supresion','pulm_cronica','hepatica_cronica','cancer','asma','nombre_responsable','cargo_responsable',
           'ing_encamamiento', 'UCI', 'observacion', 'ref_hosp', 'cual_hospital', 'fecha_egreso', 'recibio_vacuna', 'tipo_vacuna1',
           'fecha_vacunacion_dosis1', 'fecha_vacunacion_dosis2']

columnas = ['Nombre paciente','Sexo','Edad años','Fecha de Nacimiento','Municipio','Distrito de salud',
            'Direccion de residencia',  'Departamento','Contacto paciente',
           'Área de salud', 'Servicio de salud', 'Fecha de notificación','Fecha inicio de síntomas','Embarazada', 'Clasificación paciente',
           'Condición de egreso','No. Ficha Epidemiológica', 'Fecha toma de muestra','Toma de muestra','Tipo de muestra','Virus detectado', 
           'CUI Paciente','Vigilancia ETI','Trabajador de salud','Pueblo','Ocupación','Escolaridad', 
           'Disnea','Estridor','Dolor muscular', 'Dolor de cabeza','Malestar general','Fiebre','Odinofagia',
           'Rinorrea','Tos',
           'Disfunción neuromuscular','Diabetes','Antecedentes de fiebre','Cardiopatía Crónica (hipertensión arterial)',
           'Obesidad','Insuficiencia renal crónica','Inmunosupresión','EPOC','Enfermedad hepática crónica','Cáncer','Asma','Nombre responsable','Cargo responsable',
           'Encamamiento', 'UCI', 'Observacion', 'Referido hospital', 'Cual hospital', 'Fecha egreso', 'recibio_vacuna', 'tipo_vacuna1',
           'fecha_vacunacion_dosis1', 'fecha_vacunacion_dosis2']
## Estandarizar nombre de variables
old_names = columnas1[2:]
new_names = columnas[1:]
names = {}
for old_name, new_name in zip(old_names, new_names):
    names[old_name] = new_name
names['nombres'] = 'Nombre paciente'
names['apellidos'] = 'Apellido paciente'
epiweb.rename(columns = names, inplace=True)

#Transformación de variables
## De DMS o DAS a LocationID
print('Agregando locationIds')
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].str.lower()
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].replace("á", "a", regex=True) 
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].replace("é", "e", regex=True) 
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].replace("í", "i", regex=True)
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].replace("ó", "o", regex=True)
epiweb['Distrito de salud'] = epiweb['Distrito de salud'].replace("ú", "u", regex=True) 

epiweb['Área de salud'] = epiweb['Área de salud'].str.lower()
epiweb['Área de salud'] = epiweb['Área de salud'].replace("á", "a", regex=True) 
epiweb['Área de salud'] = epiweb['Área de salud'].replace("é", "e", regex=True) 
epiweb['Área de salud'] = epiweb['Área de salud'].replace("í", "i", regex=True)
epiweb['Área de salud'] = epiweb['Área de salud'].replace("ó", "o", regex=True)
epiweb['Área de salud'] = epiweb['Área de salud'].replace("ú", "u", regex=True) 

losLocationId = []
for index, row in epiweb.iterrows():
    if len(locationsId.loc[locationsId['Área de salud'] == row['Área de salud']].loc[locationsId['Distrito de salud'] == row['Distrito de salud']]) >0 :
        losLocationId.append(locationsId.loc[locationsId['Área de salud'] == row['Área de salud']].loc[locationsId['Distrito de salud'] == row['Distrito de salud']]['dmsID'].values[0])
    else:
        losLocationId.append(locationsId.loc[locationsId['Área de salud'] == row['Área de salud']]['dasID'].unique().tolist().pop())

epiweb['locationsId'] = losLocationId

# dms['name'] = dms['name'].apply(lambda x: x[4:]).str.lower()
# dms['name'] = dms['name'].apply(lambda x: x[:-1] if x[-1] == ' ' else x)
# dms.rename(columns={'id':'dmsid'}, inplace=True)

# das['name'] = das['name'].apply(lambda x: x[4:]).str.lower()
# das.rename(columns={'id':'dasid'}, inplace=True)

# dms['name'] = dms['name'].replace("á", "a", regex=True) 
# dms['name'] = dms['name'].replace("é", "e", regex=True) 
# dms['name'] = dms['name'].replace("í", "i", regex=True)
# dms['name'] = dms['name'].replace("ó", "o", regex=True)
# dms['name'] = dms['name'].replace("ú", "u", regex=True) 

# das['name'] = das['name'].replace("á", "a", regex=True) 
# das['name'] = das['name'].replace("é", "e", regex=True) 
# das['name'] = das['name'].replace("í", "i", regex=True)
# das['name'] = das['name'].replace("ó", "o", regex=True)
# das['name'] = das['name'].replace("ú", "u", regex=True) 
# das['name'] = das['name'].replace("sur oriente", "sur oriental", regex=True) 
# das['name'] = das['name'].replace("peten sur occidente", "peten sur occidental", regex=True) 

# epiweb = epiweb.join(dms.set_index('name'), on = 'Distrito de salud')
# epiweb = epiweb.join(das.set_index('name'), on = 'Área de salud')

epiweb = epiweb[~epiweb.index.duplicated(keep='first')]

## Formato de fechas
### Obtener año actual para corregir fechas de los 1900s
print('Formateando fechas')
year = int(time.strftime('%y'))
#epiweb['Fecha de Nacimiento'] = epiweb['Fecha de Nacimiento'].apply(lambda x: x[:-2] + '20' + x[-2:] if int(x[-2:]) <= year else  x[:-2] + '19' + x[-2:] )
epiweb['Fecha de Nacimiento'] = pd.to_datetime(epiweb[['Fecha de Nacimiento']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
epiweb['Fecha de Nacimiento'] = epiweb['Fecha de Nacimiento'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else pd.to_datetime(date.today()).strftime('%Y-%m-%dT00:00:00.000Z'))

if len(epiweb[['Fecha de notificación']].stack()) != 0:
    epiweb['Fecha de notificación'] = pd.to_datetime(epiweb[['Fecha de notificación']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['Fecha de notificación'] = epiweb['Fecha de notificación'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z'))
else:
    epiweb['Fecha de notificación'] = ''

if len(epiweb[['Fecha inicio de síntomas']].stack()) != 0:
    epiweb['Fecha inicio de síntomas'] = pd.to_datetime(epiweb[['Fecha inicio de síntomas']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['Fecha inicio de síntomas'] = epiweb['Fecha inicio de síntomas'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else '')
else:
    epiweb['Fecha inicio de síntomas'] = ''

if len(epiweb[['Fecha toma de muestra']].stack()) != 0:
    epiweb['Fecha toma de muestra'] = pd.to_datetime(epiweb[['Fecha toma de muestra']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['Fecha toma de muestra'] = epiweb['Fecha toma de muestra'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else '')
else:
    epiweb['Fecha toma de muestra'] = ''

if len(epiweb[['Fecha egreso']].stack()) != 0:
    epiweb['Fecha egreso'] = pd.to_datetime(epiweb[['Fecha egreso']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['Fecha egreso'] = epiweb['Fecha egreso'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else '')
else:
    epiweb['Fecha egreso'] = ''

if len(epiweb[['fecha_vacunacion_dosis1']].stack()) != 0:
    epiweb['fecha_vacunacion_dosis1'] = pd.to_datetime(epiweb[['fecha_vacunacion_dosis1']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['fecha_vacunacion_dosis1'] = epiweb['fecha_vacunacion_dosis1'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else '')
else:
    epiweb['fecha_vacunacion_dosis1'] = ''

if len(epiweb[['fecha_vacunacion_dosis2']].stack()) != 0:
    epiweb['fecha_vacunacion_dosis2'] = pd.to_datetime(epiweb[['fecha_vacunacion_dosis2']].stack(), format='%d/%m/%Y', errors='coerce').unstack()
    epiweb['fecha_vacunacion_dosis2'] = epiweb['fecha_vacunacion_dosis2'].apply(lambda x: x.strftime('%Y-%m-%dT00:00:00.000Z') if not pd.isnull(x) else '')
else:
    epiweb['fecha_vacunacion_dosis2'] = ''

## Servicio de salud
print('Transformando servicio de salud')
epiweb['Servicio de salud'] = epiweb['Servicio de salud'].replace("\xa0", "", regex=True)

## Ocupación
epiweb['Ocupación'] = np.select(
    [
        epiweb['Ocupación'] == 'Albañiles',
        epiweb['Ocupación'] == 'Carniceros, pescaderos y afines',
        epiweb['Ocupación'] == 'Personal directivo de la administración pública',
        epiweb['Ocupación'] == 'Comerciantes de tiendas',
        epiweb['Ocupación'] == 'Ama de casa',
        epiweb['Ocupación'] == 'Técnicos de laboratorios médicos',
        epiweb['Ocupación'] == 'Limpiadores y asistentes de oficinas, hoteles y otros establecimientos',
        epiweb['Ocupación'] == 'Gerentes de hoteles',
        epiweb['Ocupación'] == 'Recepcionistas de hoteles',
        epiweb['Ocupación'] == 'Supervisores de mantenimiento y limpieza en oficinas, hoteles y otros establecimientos',
        epiweb['Trabajador de salud'] == 'SI',
        epiweb['Ocupación'] == 'Pescadores, cazadores, tramperos y recolectores de subsistencia',
        epiweb['Ocupación'] == 'Cazadores y tramperos',
        epiweb['Ocupación'] == 'Limpiadores y asistentes domésticos',
        epiweb['Ocupación'] == 'Oficinistas generales'
    ],
    [
        "LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_ALBANIL",
        "LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_BUTCHER",
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_CIVIL_SERVANT',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_DEPENDIENTE_DE_TIENDA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_FARMER',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HEALTH_LABORATORY_WORKER',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HEALTH_CARE_WORKER',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HUNTER',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HUNTER',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_LIMPIEZA_DOMESTICA',
        'LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_OFICINA'

    ],
    default=''
)

## Estado de embarazo
print('Tansformando estado de embarazo')
epiweb['Embarazada'] = np.select(
    [
        epiweb['Embarazada'] == 'SI',
        epiweb['Embarazada'] == 'NO',
        epiweb['Embarazada'] == 'No aplica'
    ],
    [
        "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_TRIMESTER_UNKNOWN",
        "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NOT_PREGNANT",
        'LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NO_APLICA'
    ]
)

## Clasificación
print('Tansformando clasificación')
epiweb['Clasificación paciente'] = np.select(
    [
        epiweb['Clasificación paciente'] == 'Sospechoso',
        epiweb['Clasificación paciente'] == 'Confirmado',
        epiweb['Clasificación paciente'] == 'Confirmado por nexo epidemiológico',
        epiweb['Clasificación paciente'] == 'Probable',
        epiweb['Clasificación paciente'] == 'Descartado'
    ],
    [
        "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
        "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED",
        'LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMADO_POR_NEXO',
        'LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE',
        'LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED'   
    ]
)

## Condición del paciente
print('Tansformando condición')
epiweb['Condición de egreso'] = np.select(
    [
        epiweb['Condición de egreso'] == 'Vivo',
        epiweb['Condición de egreso'] == 'Muerto'
    ],
    [
        "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",
        'LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED'   
    ]
)

## Toma muestra
print('Tansformando toma de muestra')
epiweb['Toma de muestra'] = np.select(
    [
        epiweb['Toma de muestra'] == 'SI',
        epiweb['Toma de muestra'] == 'NO'
    ],
    [
        '1',
        '2'
    ]
)

## Tipo de muestra
print('Tansformando tipo de muestra')
epiweb['Tipo de muestra'] = np.select(
    [
        epiweb['Tipo de muestra'] == 'Hisopado nasal',
        epiweb['Tipo de muestra'] == 'Hisopado nasofaríngeo',
        epiweb['Tipo de muestra'] == 'Hisopado orogaríngeo o garganta',
        epiweb['Tipo de muestra'] == 'Otros'
    ],
    [
        '1',
        '2',
        '3',
        '4'
    ],
    default=''
)

## Virus detectado
print('Tansformando virus detectado')
epiweb['Virus detectado'] = np.select(
    [
        epiweb['Virus detectado'] == 'SARS-CoV-2',
        epiweb['Virus detectado'] == 'SARS-CoV-2, Otro',
        epiweb['Virus detectado'] == 'Influenza A',
        epiweb['Virus detectado'] == 'Influenza B',
        epiweb['Virus detectado'] == 'Metapneumovirus',
        epiweb['Virus detectado'] == 'Virus Sincitial Respiratorio',
        
    ],
    [
        '1',
        '1',
        '2',
        '3',
        '4',
        '5'
    ]
)

## Resultado de muestra
epiweb['Resultado de la muestra'] = np.select(
    [
        epiweb['Virus detectado'] != '0'
    ],
    [
        '1'
    ]
)

## Trabajador de salud
print('Tansformando trabajo de salud')
epiweb['Trabajador de salud'] = np.select(
    [
        epiweb['Trabajador de salud'] == 'SI'
    ],
    [
        '1'
    ]
)

## Grupo cultural
print('Tansformando grupo cultural')
epiweb['Pueblo'] = np.select(
    [
        epiweb['Pueblo'] == 'Maya',
        epiweb['Pueblo'] == 'Ladino / Mestizo',
        epiweb['Pueblo'] == 'Garifuna',
        epiweb['Pueblo'] == 'Xinca',
        epiweb['Pueblo'] == 'Otros'
    ],
    [
        '1',
        '2',
        '3',
        '4',
        '5'
    ]
)

## Escolaridad
print('Tansformando escolaridad')
epiweb['Escolaridad'] = np.select(
    [
        epiweb['Escolaridad'] == 'Ninguna',
        epiweb['Escolaridad'] == 'Primaria',
        epiweb['Escolaridad'] == 'Secundaria',
        epiweb['Escolaridad'] == 'Diversificado',
        epiweb['Escolaridad'] == 'Universitario'
    ],
    [
        '1',
        '2',
        '3',
        '4',
        '5'
    ]
)

## Dirección del paciente
epiweb['Direccion de residencia'] = epiweb['Direccion de residencia'].apply(str).apply(lambda x: x[:] if x != 'nan' else  '' )

## Documento de identificación
epiweb['CUI Paciente'] = epiweb['CUI Paciente'].apply(str).apply(lambda x: x[:] if x != 'nan' else  '' )
epiweb['Documento de identificación'] = epiweb['CUI Paciente'].apply(lambda x: '1' if len(x) > 0 else '0')

## Contacto del paciente
epiweb['Contacto paciente'] = epiweb['Contacto paciente'].apply(str).apply(lambda x: x[:] if x != 'nan' else  '' )

## Sexo
print('Tansformando sexo')
epiweb['Sexo'] = np.select(
    [
        epiweb['Sexo'] == 'Femenino',
        epiweb['Sexo'] == 'Masculino'
    ],
    [
        'LNG_REFERENCE_DATA_CATEGORY_GENDER_FEMALE',
        'LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE'
    ]
)

## Vigilancia ETI
print('Tansformando vigilancia ETI')
epiweb['Vigilancia ETI'] = np.select(
    [
        epiweb['Vigilancia ETI'] == 'ETI',
        epiweb['Vigilancia ETI'] == 'IRAG'
    ],
    [
        '1',
        '2'
    ]
)

## Hospitalización
epiweb['Hospitalizado'] = ''
epiweb['Hospitalizado'] = np.select(
    [
        epiweb['Encamamiento'] == 'SI',
        epiweb['Vigilancia ETI'] == '2',
        epiweb['Observacion'] == 'SI',
        epiweb['UCI'] == 'SI'
    ],
    [
        '1',
        '1',
        '1',
        '1'
    ],
    default=''
)

## Vigilancia ETI
print('Tansformando vigilancia tipo_vacuna1')
epiweb['tipo_vacuna1'] = np.select(
    [
        epiweb['tipo_vacuna1'] == 'Moderna',
        epiweb['tipo_vacuna1'] == 'Astra Zeneca/Oxford',
        epiweb['tipo_vacuna1'] == 'Sputnik',
        epiweb['tipo_vacuna1'] == 'Pfizer Biontech',
        epiweb['tipo_vacuna1'] == 'Otras (especifique)',
        epiweb['tipo_vacuna1'] == 'Jhonson&Jhonson'
    ],
    [
        'moderna',
        'astrazeneca',
        'sputnik',
        'pfizer',
        'otro',
        'jhonson&jhonson'
    ]
)

# Transformacion a JSON
print('Convirtiendo a json')
## lista donde guardaremos cada uno de los casos en forma de diccionario
cases = []
samples = []
samples
for index, row in epiweb.iterrows():
    sample = {}
    case = {
        'firstName': row['Nombre paciente'],
        'lastName' : row['Apellido paciente'],
        'visualId': 'RCC-2020-99999',
        'gender' : row['Sexo'],
        'age': {'years': row['Edad años']},
        'addresses': [{
            'addressLine1' : row['Direccion de residencia'],
            'typeId': 'LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_USUAL_PLACE_OF_RESIDENCE',
            'date': row['Fecha de notificación'],
        }],
        'dateOfReporting': row['Fecha de notificación'],
        'outbreakId' : outbreakId, #rastreo Guatemala central
        'classification' : row['Clasificación paciente'], # clasificacion
        'outcomeId' : row['Condición de egreso'], # condicion 
        'dateOfOutcome' : row['Fecha de notificación'], #Fecha de notificación
        #'dateOfOnset': row['Fecha inicio de síntomas'],  #Fecha de inicio de sintomas
        # Inicia informacion de sintomas y enfermedades
        'questionnaireAnswers': {
            'Case_WhichForm': [{'value': 'Ficha Epidemiológica 1'}], 

            ## Aca iría la información de la unidad notificadora de datos ##

            #"FE101unidad_notificadora": [{ #Necesario para especificar campamento
            #    "value": "1"    #Correlativo MSPAS.
            #}],
            #"FE10101direccion_de_area_de_salud": [{  # Aca se pone que DAS es
            #    "value": "278" # guatemala central
            #}],

            ## termina informacion de la unidad notificadora ##

            'FE103no_de_ficha_de_notificacion': [{'value': row['No. Ficha Epidemiológica']}], # ID ficha de notificacíon
            "FE111grupo_cultural": [
                {
                    "value": row['Pueblo'] 
                }
            ],
            "FE112escolaridad": [
                {
                    "value": row['Escolaridad'] 
                }
            ],
            'FE113enfermedades_asociadas': [{'value': []}], #Otro
            'FE114sintomas': [{'value': []}], #Otro
            'servicio_de_salud': [
                {
                    'value': row['Servicio de salud']
                }
            ],
        }
    }
    # INFORMACION PERSONAL
    if row['Embarazada'] != 0:
        case['pregnancyStatus'] = row['Embarazada']

    if row['Contacto paciente'] != 'Sin dato':
        case['addresses'][0]['phoneNumber'] = row['Contacto paciente']

    if row['CUI Paciente'] != '':
        case['questionnaireAnswers']["FE10801numero_de_documento_cui"] =  [{ "value": row['CUI Paciente']}]
        case['questionnaireAnswers']["FE108documento_de_identificacion"] =  [{ "value": '1'}]

    # INFORMACION DE UBICACION
    case['addresses'][0]['locationId'] = row['locationsId']

    # INFORMACION EPIDEMIOLOGICA
    if row['Fecha inicio de síntomas'] != '':
        case['dateOfOnset'] = row['Fecha inicio de síntomas']
    else:
        case['dateOfOnset'] = row['Fecha de notificación']

    if row['Vigilancia ETI'] != '0':
        case['questionnaireAnswers']["FE124tipo_de_vigilancia"] =  [{ "value": [row['Vigilancia ETI']]}]

    if row['Toma de muestra'] != '0':
        case['questionnaireAnswers']['FE121se_tomo_una_muestra_respiratoria'] = [{"value": row['Toma de muestra']}]

    if row['Fecha toma de muestra'] != '':
        case['questionnaireAnswers']['FE12102fecha_y_hora_de_toma_de_la_muestra'] = [{"value": row['Fecha toma de muestra']}]
        sample['dateSampleTaken'] = row['Fecha toma de muestra']
        sample['sampleIdentifier'] = row['No. Ficha Epidemiológica']

    if row['Tipo de muestra'] == '1' or row['Tipo de muestra'] == '2' or row['Tipo de muestra'] == '3' or row['Tipo de muestra'] == '4':
        case['questionnaireAnswers']["FE12101tipo_de_muestra"] =  [{ "value": [row['Tipo de muestra']]}]
    else:
        case['questionnaireAnswers']["FE12101tipo_de_muestra"] =  [{ "value": ['4']}]
        case['questionnaireAnswers']["FE12102especifique"] =  [{ "value": row['Tipo de muestra'] }]
    if row['Tipo de muestra'] == '1':
        sample['sampleType'] = 'LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASAL'
    elif row['Tipo de muestra'] == '2':
        sample['sampleType'] = 'LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASOFARINGEO'

    if row['Resultado de la muestra'] != '0':
        case['questionnaireAnswers']['FE12103resultado_de_la_muestra'] = [{"value": row['Resultado de la muestra']}]

    if row['Virus detectado'] != '0':
        case['questionnaireAnswers']['FE12103resultado_de_la_muestra'] = [{"value": row['Virus detectado']}]
    if row['Virus detectado'] == '1':
        sample['result'] = 'LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE'
        sample['status'] = 'LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_STATUS_COMPLETED'

    if row['Trabajador de salud'] != '0':
        case['questionnaireAnswers']['FE125la_persona_es_un_trabajador_de_salud'] = [{"value": row['Trabajador de salud']}]
        
    if not pd.isnull(row['Nombre responsable']):
        case['questionnaireAnswers']['FE104responsable_de_llenado_de_instrumento_nombre_completo'] = [{'value':row['Nombre responsable']}]
    else:
        case['questionnaireAnswers']['FE104responsable_de_llenado_de_instrumento_nombre_completo'] = [{'value':'Sin datos EPIWEB'}]
        
    if not pd.isnull(row['Cargo responsable']):
        case['questionnaireAnswers']['FE105cargo_del_trabajador_que_notifica'] = [{'value':row['Cargo responsable']}]
    else:
        case['questionnaireAnswers']['FE105cargo_del_trabajador_que_notifica'] = [{'value':'Sin datos EPIWEB'}]
    
    if row['Ocupación'] != '':
        case['occupation'] = row['Ocupación']

    if row['Hospitalizado'] != '':
        case['questionnaireAnswers']["FE130la_persona_fue_hospitalizada"] =  [{ "value": row['Hospitalizado']}]
        if row['Referido hospital'] == 'SI':
            case['questionnaireAnswers']["FE13006referido_a_otro_hospital"] =  [{ "value": '1'}]
        if not pd.isnull(row['Cual hospital']):
            case['questionnaireAnswers']["FE13006cual"] =  [{ "value": row['Cual hospital']}]
        if row['Fecha egreso'] != '':
            case['questionnaireAnswers']["FE13007fecha_de_egreso"] =  [{ "value": row['Fecha egreso']}]
        if row['Condición de egreso'] == "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE":
            case['questionnaireAnswers']["FE13007condicion_del_paciente_al_egreso"] =  [{ "value": '1'}]
        if row['Condición de egreso'] == 'LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED':
            case['questionnaireAnswers']["FE13007condicion_del_paciente_al_egreso"] =  [{ "value": '2'}]
    
    if row['fecha_vacunacion_dosis1'] != '':
        case['questionnaireAnswers']["recibio_vacuna_de_covid_19"] = [{ "value": 'si'}]
        case['questionnaireAnswers']["vacuna_recibida"] = [{ "value": row['tipo_vacuna1']}]
        case['questionnaireAnswers']["fecha_primera_dosis"] = [{ "value": row['fecha_vacunacion_dosis1']}]
        if row['fecha_vacunacion_dosis2'] != '':
            case['questionnaireAnswers']["fecha_segunda_dosis"] = [{ "value": row['fecha_vacunacion_dosis2']}]



    # ENFERMEDADES ASOCIADAS
    if row['Diabetes'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('1')
    if row['EPOC'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('2')
    if row['Insuficiencia renal crónica'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('3')
    if row['Cáncer'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('4')   
    if row['Asma'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('5') 
    if row['Inmunosupresión'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('6') 
    if row['Enfermedad hepática crónica'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('8') 
    if row['Cardiopatía Crónica (hipertensión arterial)'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('9') 
    if row['Disfunción neuromuscular'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('10') 
    if row['Obesidad'] == 'SI':
        case['questionnaireAnswers']['FE113enfermedades_asociadas'][0]['value'].append('11') 

    # SINTOMAS
    if row['Fiebre'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('1')
    if row['Antecedentes de fiebre'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('2') 
    if row['Malestar general'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('3') 
    if row['Dolor muscular'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('4') 
    if row['Dolor de cabeza'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('5')
    if row['Tos'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('6')
    if row['Odinofagia'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('7')
    if row['Rinorrea'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('8')
    if row['Rinorrea'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('9')
    if row['Disnea'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('11')   
    if row['Estridor'] == 'SI':
        case['questionnaireAnswers']['FE114sintomas'][0]['value'].append('12') 
    cases.append(case)
    samples.append(sample)

#print(f"Se transformaron {len(cases)} casos exitosamente.")
# USO DEL API DE GO.DATA
print('Iniciando sesión en el API de Go.Data')
## Login
loginParams = {'email':email,'password':password}
r = requests.post(link+'/users/login', data=loginParams, verify = False)
response = r.json()
## Token para autentificación. Necesario para utilizar el API
token = response['id']
userId = response['userId']
print('Inicio de sesión exitoso')
## Activando outbreak
activeParams = {'activeOutbreakId': outbreakId}
r = activeOutbreak = requests.patch(link+'/users/'+userId+'?access_token='+token, json=activeParams, verify = False)
## Importación de casos a Go.Data
### para pruebas
#cases = cases[:5]
### Se importa un caso a la vez para que no se generen IDs repetidos
#linkCaso = link+'/outbreaks/'+outbreakId+'/cases/80091da0-c4f7-44bb-85b7-cf8bdefd1fe5'+'?access_token='+token
cases = cases[args.ignorar:]
print('Inicio de importación de casos')
for i, case in enumerate(cases):
    print(f'Importando caso {i+1}/{len(cases)}', time.strftime('%d-%m-%y %H:%M:%S'))
    r = requests.post(link+'/outbreaks/' + outbreakId+'/cases?access_token='+token, json=case, verify = False)
    if r.status_code == 200:
        fk = r.json()['id']
        if 'dateSampleTaken' in samples[i-1]:
            lab = requests.post(link+'/outbreaks/'+outbreakId+'/cases/'+fk+'/lab-results?access_token='+token, json=samples[i-1], verify=False)
            if lab.status_code != 200:
                print(lab.json())
                print(samples[i-1])
    else:
        print(r.json())
        print(case)
        sys.exit()
print('Importación de casos exitosos')
print('Script finalizado.\n', time.strftime('%d-%m-%y %H:%M:%S'))
