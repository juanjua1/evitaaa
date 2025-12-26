import pandas as pd
import glob
import os

# --- 1️⃣ Directorio base (donde está el script) ---
directorio_script = os.path.dirname(os.path.abspath(__file__))

# --- 2️⃣ Cargar archivos de REPORTES ---
ruta_reportes = os.path.join(directorio_script, "reportes", "*.csv")
archivos_reportes = glob.glob(ruta_reportes)
df_reportes = []

for archivo in archivos_reportes:
    temp = pd.read_csv(archivo, sep=';', encoding='utf-8', dtype=str)
    #temp = temp[['Campaña', 'Lote', 'Inicio', 'Cliente', 'Sentido',
                 #'Nombre Agente', 'TalkingTime', 'Tipificación', 'Causa Terminación']]
    df_reportes.append(temp)

df_reportes = pd.concat(df_reportes, ignore_index=True)
print(f"✅ Cargados {len(archivos_reportes)} archivos de REPORTES.")
print(f"✅ Cargados {len(df_reportes)} elementos de REPORTES.")

# --- 3️⃣ Cargar df de REPORTES ---

def normalizar_numeros_columna(df, columna):
    def procesar_numero(numero):
        if pd.isna(numero):
            return numero  # Mantener NaN si existe

        numero = str(numero).strip()

        # Eliminar el "0" al principio si está presente
        if numero.startswith("0"):
            numero = numero[1:]

        # Eliminar el prefijo "90" si está presente
        if numero.startswith("90"):
            numero = numero[2:]

        # Procesar números que empiezan con "11" (Buenos Aires)
        if numero.startswith("11"):
            if numero[2:4] == "15":  # Si "15" sigue a la característica
                numero = "11" + numero[4:]
        else:
            # Procesar otras características (3 o 4 dígitos)
            if len(numero) >= 5:
                caracteristica = numero[:3]
                if numero[3:5] == "15":  # Característica de 3 dígitos
                    numero = caracteristica + numero[5:]
                elif len(numero) > 4 and numero[:4].isdigit() and numero[4:6] == "15":  # Característica de 4 dígitos
                    caracteristica = numero[:4]
                    numero = caracteristica + numero[6:]
        return numero

    # Aplicar la función fila por fila y reemplazar en la misma columna
    df[columna] = df[columna].apply(procesar_numero)

    return df

df_reportes_normalizado = normalizar_numeros_columna(df_reportes, 'Cliente')
print(f"✅ DF de reportes normalizado.")


# --- 4️⃣ Cargar archivos de BASES ---
ruta_bases = os.path.join(directorio_script, "bases", "*.csv")
archivos_bases = glob.glob(ruta_bases)
df_bases = []

for archivo in archivos_bases:
    temp = pd.read_csv(archivo, sep=';', encoding='utf-8', dtype=str)
    #temp = temp[['id', 'Cliente', 'Telefono', 'Campaña']]
    df_bases.append(temp)

df_bases = pd.concat(df_bases, ignore_index=True)
df_bases = df_bases.drop_duplicates(subset=['Linea2'], keep='first')

print(f"✅ Cargados {len(archivos_bases)} archivos de BASES.")
print(f"✅ Cargados {len(df_bases)} elementos de BASES.")


# --- 5️⃣ Hacer el JOIN ---

resultado = pd.merge(
    df_bases,
    df_reportes_normalizado,
    left_on='Linea2',
    right_on='Cliente',
    how='inner' 
)
print(f"✅ Cargados {len(resultado)} elementos de RESULTADOS.")

# --- 6️⃣ Filtrar y procesar columnas ---
columnas_a_mantener = [
    "DNI",
    "Inicio",
    "idInteraccion",
    "Nombre Agente",
    "Tipificación",
    "Cliente",
    "Causa Terminación"
]

resultado_filtrado = resultado[columnas_a_mantener].copy()
print(f"✅ Columnas filtradas: {list(resultado_filtrado.columns)}")

# --- 7️⃣ Convertir fecha y crear columnas de Fecha y Hora ---
resultado_filtrado['Inicio'] = pd.to_datetime(resultado_filtrado['Inicio'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
resultado_filtrado['Fecha'] = resultado_filtrado['Inicio'].dt.date
resultado_filtrado['Hora'] = resultado_filtrado['Inicio'].dt.time
print(f"✅ Columnas 'Fecha' y 'Hora' creadas desde 'Inicio'.")

# --- 8️⃣ Reorganizar columnas finales ---
columnas_a_mantener_2 = [
    "DNI",
    "Cliente",
    'Fecha',
    'Hora',
    "idInteraccion",
    "Nombre Agente",
    "Tipificación",
    "Causa Terminación"
]

resultado_filtrado = resultado_filtrado[columnas_a_mantener_2]
print(f"✅ Columnas reorganizadas: {list(resultado_filtrado.columns)}")

# --- 9️⃣ Guardar resultado final ---
nombre_salida = "resultado_final.csv"
ruta_salida = os.path.join(directorio_script, nombre_salida)
resultado_filtrado.to_csv(ruta_salida, sep=';', index=False, encoding='utf-8-sig')
print(f"✅ Archivo de resultados guardado en: {ruta_salida}")
print(f"✅ Total de registros en archivo final: {len(resultado_filtrado)}")