import pandas as pd

df = pd.read_csv("evaluaciones_modelo_gemini.csv")
df.head()
df["Agente"] = df["Agente"].str.removesuffix(".json")


df2 = pd.read_csv("resultado_final.csv", sep=";", encoding="utf-8")
df2.head()
columnas = ["Nombre Agente", "idInteraccion", "Fecha", "Hora", "Cliente", "Tipificación"]
df2 = df2[columnas]

df_final = df.merge(df2, 
                    left_on="Agente", 
                    right_on="idInteraccion", 
                    how="left")

df_final["idInteraccion"].notna().sum()
df_final.head()
df_final.to_csv("powerbi.csv", index=False, encoding="utf-8")
