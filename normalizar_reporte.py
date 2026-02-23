import pandas as pd
import unicodedata
import re

def quitar_tildes(s):
    return ''.join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def normalizar_texto(valor):
    if pd.isna(valor):
        return valor

    s = str(valor)

    # 1️⃣ Quitar tildes
    s = quitar_tildes(s)

    # 2️⃣ Pasar a minúsculas
    s = s.lower()

    # 3️⃣ Quitar plural 'es' (antes que 's')
    #    necesidades -> necesidad
    s = re.sub(r"\b([a-z]+?)es\b", r"\1", s)

    # 4️⃣ Quitar plural 's'
    #    ventas -> venta
    s = re.sub(r"\b([a-z]+?)s\b", r"\1", s)

    # 5️⃣ Title Case
    s = s.title()

    return s

# ========= USO =========
df = pd.read_csv("evaluaciones_gemini.csv")

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].apply(normalizar_texto)

df.to_csv("evaluaciones_gemini_excel.csv", sep=";", encoding="utf-8-sig", index=False)
df.to_csv("evaluaciones_gemini_normalizado.csv", index=False, encoding="utf-8")

print("Normalización aplicada correctamente")
