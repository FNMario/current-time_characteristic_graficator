# Graficador de curvas
Este es un proyecto para crear un graficador de curvas partiendo de un unifilar en formato tabular en google sheets con las siguientes columnas:
- sector
- carga
- carga de emergencia (SI/NO)
- nombre
- I_n
- nombre del conductor
- vacío
- S del conductor
- I_adm del conductor
- K del conductor
- vacío
- nombre de la termica
- I_t de la termica
- I_cc de la termica
- I_r de la termica
- t_r de la termica
- I_sd de la termica
- t_sd de la termica
- I_i de la termica
- curva de la termica
- nombre del guardamotor
- I_t del guardamotor
- I_cc del guardamotor
- curva del guardamotor
- nombre del fusible
- I_f del fusible
- alimentador (barra a la que se conecta. Si no se conecta a ninguna barra dejar vacío)

*IMPORTANTE:* El encabezado debe estar en el rango B3:AB3 y los datos comenzar en la fila 5

## Configuración
El proyecto requiere de la siguiente configuración:
- google_sheets_name.txt: un archivo de texto que contiene el url de la hoja de google sheets que contiene los datos.

## Instalación
1. Instalar pyhton 10 o superior.
2. Para crear el entorno virtual de python, abrir una terminal y ejecutar:
### Linux / maxOS
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Windows
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso
Para ejecutar el script de python, abrir una terminal y ejecutar:
```
python curvas.py
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.