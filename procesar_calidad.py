"""
Script para procesar los 3 archivos de calidad:
- Acumuladores: Tiempos (Break, Coaching, Administrativo, Baño, etc.)
- Solicitudes: Ventas
- Basurita: Llamadas
"""

import pandas as pd
import json
import os
from datetime import datetime
import glob

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_SALIDA = os.path.join(RUTA_BASE, 'datos_calidad')
os.makedirs(RUTA_SALIDA, exist_ok=True)

def cargar_mapeo_vendedores():
    ruta_listado = os.path.join(RUTA_BASE, 'LISTADO-DE-VENDEDORES.csv')
    mapeo = {}
    if os.path.exists(ruta_listado):
        try:
            df = pd.read_csv(ruta_listado, encoding='latin-1')
            df.columns = ['Usuario', 'Nombre', 'Equipo'] + [f'col_{i}' for i in range(len(df.columns)-3)]
            df = df[['Usuario', 'Nombre', 'Equipo']].dropna(subset=['Usuario'])
            df = df[df['Usuario'] != 'Usuario']
            for _, row in df.iterrows():
                usuario = str(row['Usuario']).lower().strip().replace(' ', '')
                mapeo[usuario] = {'nombre': str(row['Nombre']).strip(), 'equipo': str(row['Equipo']).strip()}
            print(f"✅ Mapeo cargado: {len(mapeo)} agentes")
        except Exception as e:
            print(f"⚠️ Error cargando mapeo: {e}")
    return mapeo

def tiempo_a_segundos(tiempo_str):
    if pd.isna(tiempo_str) or tiempo_str == '' or tiempo_str == '0':
        return 0
    try:
        tiempo_str = str(tiempo_str).strip()
        partes = tiempo_str.split(':')
        if len(partes) == 3:
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
        elif len(partes) == 2:
            return int(partes[0]) * 60 + int(partes[1])
        return int(float(tiempo_str))
    except:
        return 0

def segundos_a_tiempo(segundos):
    if segundos == 0:
        return "00:00:00"
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def procesar_tiempos(ruta_archivo, mapeo):
    print(f"\n⏱️ Procesando TIEMPOS...")
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        return {'por_vendedor': [], 'totales': {}}
    try:
        df = pd.read_csv(ruta_archivo, encoding='latin-1', sep=';')
        df.columns = df.columns.str.replace('ï»¿', '').str.strip()
        col_agente = next((c for c in df.columns if c.lower() == 'agente'), None)
        if not col_agente:
            return {'por_vendedor': [], 'totales': {}}
        
        columnas_tiempo = {'break': None, 'coaching': None, 'administrativo': None, 'baño': None, 
                          'llamada_manual': None, 'disponible': None, 'logueo': None, 'no_disponible': None, 'almuerzo': None}
        for c in df.columns:
            cl = c.lower()
            if 'break' in cl and 'tipo' not in cl: columnas_tiempo['break'] = c
            elif 'coaching' in cl: columnas_tiempo['coaching'] = c
            elif 'administrativo' in cl: columnas_tiempo['administrativo'] = c
            elif 'baño' in cl or 'bano' in cl: columnas_tiempo['baño'] = c
            elif 'manual' in cl: columnas_tiempo['llamada_manual'] = c
            elif 'disponible' in cl and 'no' not in cl and 'tiempo' in cl: columnas_tiempo['disponible'] = c
            elif 'tiempo real' in cl and 'logueo' in cl: columnas_tiempo['logueo'] = c
            elif 'no disponible' in cl: columnas_tiempo['no_disponible'] = c
            elif 'lunch' in cl or 'almuerzo' in cl: columnas_tiempo['almuerzo'] = c
        
        print(f"   Columnas: {[k for k,v in columnas_tiempo.items() if v]}")
        datos_vendedor = []
        totales = {k: 0 for k in columnas_tiempo.keys()}
        totales['total_agentes'] = 0
        
        for agente in df[col_agente].dropna().unique():
            agente_str = str(agente).strip()
            if not agente_str or agente_str.lower() == 'nan': continue
            df_a = df[df[col_agente] == agente]
            info = mapeo.get(agente_str.lower().replace(' ', ''), {})
            registro = {'agente': agente_str, 'vendedor': info.get('nombre', agente_str.upper()), 'equipo': info.get('equipo', 'Sin Equipo')}
            for key, col in columnas_tiempo.items():
                if col and col in df_a.columns:
                    val = df_a[col].apply(tiempo_a_segundos).sum()
                    registro[f'{key}_seg'] = int(val)
                    registro[f'{key}_fmt'] = segundos_a_tiempo(val)
                    totales[key] += val
                else:
                    registro[f'{key}_seg'] = 0
                    registro[f'{key}_fmt'] = "00:00:00"
            tiempo_aux = sum(registro.get(f'{k}_seg', 0) for k in ['break', 'coaching', 'administrativo', 'baño', 'almuerzo'])
            registro['tiempo_auxiliar_seg'] = tiempo_aux
            registro['tiempo_auxiliar_fmt'] = segundos_a_tiempo(tiempo_aux)
            t_log = registro.get('logueo_seg', 0)
            t_disponible = max(t_log - tiempo_aux, 0)
            registro['disponible_seg'] = t_disponible
            registro['disponible_fmt'] = segundos_a_tiempo(t_disponible)
            registro['pct_productivo'] = round((t_log - tiempo_aux) / t_log * 100, 1) if t_log > 0 else 0
            datos_vendedor.append(registro)
            totales['total_agentes'] += 1
        
        for key in columnas_tiempo.keys():
            totales[f'{key}_fmt'] = segundos_a_tiempo(totales[key])
            if totales['total_agentes'] > 0:
                totales[f'{key}_prom'] = int(totales[key] / totales['total_agentes'])
                totales[f'{key}_prom_fmt'] = segundos_a_tiempo(totales[f'{key}_prom'])
        print(f"   ✅ {len(datos_vendedor)} agentes")
        return {'por_vendedor': datos_vendedor, 'totales': totales}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'por_vendedor': [], 'totales': {}}

def procesar_ventas(ruta_archivo):
    print(f"\n💼 Procesando VENTAS...")
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        return {'por_vendedor': [], 'totales': {}, 'por_supervisor': []}
    try:
        df = pd.read_csv(ruta_archivo, encoding='latin-1')
        col_vendedor = col_supervisor = col_estado = None
        for c in df.columns:
            cl = c.lower()
            if 'vendedor' in cl: col_vendedor = c
            elif 'supervisor' in cl: col_supervisor = c
            elif 'estado' in cl and 'solicitud' in cl: col_estado = c
        if not col_vendedor or not col_estado:
            return {'por_vendedor': [], 'totales': {}, 'por_supervisor': []}
        
        df['estado_norm'] = df[col_estado].astype(str).str.upper()
        df['es_aprobada'] = df['estado_norm'].str.contains('APROB', na=False)
        df['es_cancelada'] = df['estado_norm'].str.contains('CANCEL', na=False)
        df['es_preventa'] = df['estado_norm'].str.contains('PREVENTA', na=False)
        
        total = len(df)
        aprob = int(df['es_aprobada'].sum())
        num_vend = df[col_vendedor].nunique()
        prom_esp = round(total / num_vend, 1) if num_vend > 0 else 0
        prom_aprob_esp = round(aprob / num_vend, 1) if num_vend > 0 else 0
        
        totales = {'total_ventas': total, 'total_aprobadas': aprob, 'total_canceladas': int(df['es_cancelada'].sum()),
                   'total_preventa': int(df['es_preventa'].sum()), 'num_vendedores': num_vend,
                   'promedio_ventas_esperado': prom_esp, 'promedio_aprobadas_esperado': prom_aprob_esp,
                   'tasa_aprobacion_global': round(aprob/total*100, 1) if total > 0 else 0}
        
        datos_vendedor = []
        for vend in df[col_vendedor].dropna().unique():
            v_str = str(vend).strip()
            if not v_str or v_str.lower() == 'nan': continue
            df_v = df[df[col_vendedor] == vend]
            t = len(df_v)
            a = int(df_v['es_aprobada'].sum())
            sup = str(df_v[col_supervisor].dropna().iloc[0]).strip() if col_supervisor and len(df_v[col_supervisor].dropna()) > 0 else 'Sin Supervisor'
            tasa = round(a/t*100, 1) if t > 0 else 0
            estado = '🟢 Excelente' if tasa >= 70 else '🟡 Bueno' if tasa >= 50 else '🟠 Regular' if tasa >= 30 else '🔴 Bajo'
            datos_vendedor.append({'vendedor': v_str, 'supervisor': sup, 'total_ventas': t, 'aprobadas': a,
                                   'canceladas': int(df_v['es_cancelada'].sum()), 'preventa': int(df_v['es_preventa'].sum()),
                                   'tasa_aprobacion': tasa, 'dif_vs_promedio': round(t - prom_esp, 1),
                                   'dif_aprobadas_vs_esperado': round(a - prom_aprob_esp, 1), 'estado': estado})
        datos_vendedor.sort(key=lambda x: x['aprobadas'], reverse=True)
        
        datos_sup = []
        if col_supervisor:
            for sup in df[col_supervisor].dropna().unique():
                s_str = str(sup).strip()
                if not s_str or s_str.lower() == 'nan': continue
                df_s = df[df[col_supervisor] == sup]
                datos_sup.append({'supervisor': s_str, 'num_vendedores': df_s[col_vendedor].nunique(),
                                  'total_ventas': len(df_s), 'aprobadas': int(df_s['es_aprobada'].sum()),
                                  'tasa_aprobacion': round(df_s['es_aprobada'].sum()/len(df_s)*100, 1) if len(df_s) > 0 else 0})
            datos_sup.sort(key=lambda x: x['aprobadas'], reverse=True)
        print(f"   ✅ {len(datos_vendedor)} vendedores")
        return {'por_vendedor': datos_vendedor, 'totales': totales, 'por_supervisor': datos_sup}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'por_vendedor': [], 'totales': {}, 'por_supervisor': []}

def procesar_llamadas(ruta_archivo, mapeo):
    print(f"\n📞 Procesando LLAMADAS...")
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        return {'por_vendedor': [], 'totales': {}}
    try:
        df = pd.read_csv(ruta_archivo, encoding='latin-1', sep=';')
        col_agente = col_talking = col_tipif = col_origen = None
        for c in df.columns:
            cl = c.lower()
            if c == 'LoginId' or 'loginid' in cl: col_agente = c
            elif 'talkingtime' in cl or 'talking' in cl: col_talking = c
            elif c == 'Tipificación' or 'tipificación' == cl: col_tipif = c
            elif 'origen' in cl and 'corte' in cl: col_origen = c
        
        if not col_agente:
            return {'por_vendedor': [], 'totales': {}}
        
        df['talking_seg'] = pd.to_numeric(df[col_talking], errors='coerce').fillna(0) if col_talking else 0
        df['es_cortada'] = df[col_tipif].astype(str).str.upper().str.contains('CORTADA|MUDA|CORTO', na=False) if col_tipif else False
        df['corte_cliente'] = df[col_origen].astype(str).str.contains('Cliente', case=False, na=False) if col_origen else False
        df['corte_agente'] = df[col_origen].astype(str).str.contains('Agente', case=False, na=False) if col_origen else False
        df['supera_1min'] = df['talking_seg'] >= 60
        df['supera_5min'] = df['talking_seg'] >= 300
        df['menos_30seg'] = df['talking_seg'] < 30
        df['capta_atencion'] = (df['talking_seg'] >= 60) & (~df['es_cortada'])
        
        total = len(df)
        tmo = round(df['talking_seg'].mean(), 1) if total > 0 else 0
        totales = {'total_llamadas': total, 'total_cortadas': int(df['es_cortada'].sum()),
                   'pct_cortadas': round(df['es_cortada'].sum()/total*100, 1) if total > 0 else 0,
                   'supera_1min': int(df['supera_1min'].sum()), 'pct_supera_1min': round(df['supera_1min'].sum()/total*100, 1) if total > 0 else 0,
                   'supera_5min': int(df['supera_5min'].sum()), 'pct_supera_5min': round(df['supera_5min'].sum()/total*100, 1) if total > 0 else 0,
                   'menos_30seg': int(df['menos_30seg'].sum()), 'pct_menos_30seg': round(df['menos_30seg'].sum()/total*100, 1) if total > 0 else 0,
                   'capta_atencion': int(df['capta_atencion'].sum()), 'pct_capta_atencion': round(df['capta_atencion'].sum()/total*100, 1) if total > 0 else 0,
                   'tmo_global_seg': tmo, 'tmo_global_fmt': segundos_a_tiempo(int(tmo)), 'num_agentes': df[col_agente].nunique()}
        
        datos_vendedor = []
        for agente in df[col_agente].dropna().unique():
            a_str = str(agente).strip()
            if not a_str or a_str.lower() == 'nan': continue
            df_a = df[df[col_agente] == agente]
            info = mapeo.get(a_str.lower().replace(' ', ''), {})
            t_ll = len(df_a)
            cortadas = int(df_a['es_cortada'].sum())
            sup1 = int(df_a['supera_1min'].sum())
            sup5 = int(df_a['supera_5min'].sum())
            capta = int(df_a['capta_atencion'].sum())
            tmo_a = round(df_a['talking_seg'].mean(), 1) if t_ll > 0 else 0
            pct_capta = round(capta/t_ll*100, 1) if t_ll > 0 else 0
            estado = '🟢 Excelente' if pct_capta >= 50 else '🟡 Bueno' if pct_capta >= 35 else '🟠 Regular' if pct_capta >= 20 else '🔴 Bajo'
            datos_vendedor.append({'agente': a_str, 'vendedor': info.get('nombre', a_str.upper()), 'equipo': info.get('equipo', 'Sin Equipo'),
                                   'total_llamadas': t_ll, 'tmo_seg': tmo_a, 'tmo_fmt': segundos_a_tiempo(int(tmo_a)),
                                   'cortadas': cortadas, 'pct_cortadas': round(cortadas/t_ll*100, 1) if t_ll > 0 else 0,
                                   'supera_1min': sup1, 'pct_supera_1min': round(sup1/t_ll*100, 1) if t_ll > 0 else 0,
                                   'supera_5min': sup5, 'pct_supera_5min': round(sup5/t_ll*100, 1) if t_ll > 0 else 0,
                                   'menos_30seg': int(df_a['menos_30seg'].sum()), 'capta_atencion': capta, 'pct_capta_atencion': pct_capta,
                                   'corte_cliente': int(df_a['corte_cliente'].sum()), 'corte_agente': int(df_a['corte_agente'].sum()), 'estado': estado})
        datos_vendedor.sort(key=lambda x: x['total_llamadas'], reverse=True)
        print(f"   ✅ {len(datos_vendedor)} agentes")
        return {'por_vendedor': datos_vendedor, 'totales': totales}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'por_vendedor': [], 'totales': {}}

def main():
    print("=" * 60 + "\n🚀 PROCESADOR DE DATOS DE CALIDAD\n   3 Apartados: TIEMPOS | VENTAS | LLAMADAS\n" + "=" * 60)
    mapeo = cargar_mapeo_vendedores()
    
    archivos = {'acumuladores': None, 'solicitudes': None, 'interacciones': None}
    # Buscar en raíz y en carpeta Reporte-llamadas-mitrol-agostina
    ruta_agostina = os.path.join(RUTA_BASE, 'Reporte-llamadas-mitrol-agostina')
    rutas_busqueda = [RUTA_BASE, ruta_agostina]
    
    for ruta in rutas_busqueda:
        if archivos['acumuladores']: break
        for p in ['Acumuladores*.csv']:
            f = glob.glob(os.path.join(ruta, p))
            if f: archivos['acumuladores'] = f[0]; break
    
    if os.path.exists(os.path.join(RUTA_BASE, 'solicitudes.csv')): archivos['solicitudes'] = os.path.join(RUTA_BASE, 'solicitudes.csv')
    
    for ruta in rutas_busqueda:
        if archivos['interacciones']: break
        for p in ['basurita.csv', 'Detalle Interacciones*.csv', 'Detalle*.csv']:
            f = glob.glob(os.path.join(ruta, p))
            if f: archivos['interacciones'] = f[0]; break
    
    print("\n📁 Archivos:")
    for t, r in archivos.items(): print(f"   {'✅' if r else '❌'} {t}: {os.path.basename(r) if r else 'No encontrado'}")
    
    datos_tiempos = procesar_tiempos(archivos['acumuladores'], mapeo)
    datos_ventas = procesar_ventas(archivos['solicitudes'])
    datos_llamadas = procesar_llamadas(archivos['interacciones'], mapeo)
    
    resultado = {'fecha_proceso': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'tiempos': datos_tiempos, 'ventas': datos_ventas, 'llamadas': datos_llamadas}
    ruta_salida = os.path.join(RUTA_SALIDA, 'datos_calidad_procesados.json')
    
    # Convertir int64 a int para JSON
    def convert_to_native(obj):
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(i) for i in obj]
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        return obj
    
    resultado = convert_to_native(resultado)
    with open(ruta_salida, 'w', encoding='utf-8') as f: json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60 + "\n✅ COMPLETADO\n" + "=" * 60)
    t_v = datos_ventas.get('totales', {})
    t_ll = datos_llamadas.get('totales', {})
    print(f"⏱️ TIEMPOS: {len(datos_tiempos.get('por_vendedor', []))} agentes")
    print(f"💼 VENTAS: {t_v.get('total_ventas', 0)} total | {t_v.get('total_aprobadas', 0)} aprob ({t_v.get('tasa_aprobacion_global', 0)}%)")
    print(f"📞 LLAMADAS: {t_ll.get('total_llamadas', 0)} | TMO: {t_ll.get('tmo_global_fmt', '00:00:00')} | Capta: {t_ll.get('pct_capta_atencion', 0)}%")
    print(f"\n💾 Guardado: {ruta_salida}")

if __name__ == "__main__":
    main()
