"""Script temporal para actualizar LISTADO-DE-VENDEDORES.csv y credenciales_eva.csv"""
import csv, os, shutil, random, string

# Backup
shutil.copy('LISTADO-DE-VENDEDORES.csv', 'LISTADO-DE-VENDEDORES_backup.csv')
shutil.copy('credenciales_eva.csv', 'credenciales_eva_backup.csv')
print('✅ Backups creados')

# Cargar credenciales existentes para mantener passwords
creds_existentes = {}
with open('credenciales_eva_backup.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f)
    for row in reader:
        creds_existentes[row['Usuario'].strip().lower().replace('\t','')] = row

# Cargar nombres existentes del listado
nombres_existentes = {}
with open('LISTADO-DE-VENDEDORES_backup.csv', 'r', encoding='latin-1') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if row:
            usuario = row[0].strip().lower().replace('\t','')
            nombre = row[1].strip() if len(row) > 1 else ''
            nombres_existentes[usuario] = nombre

print(f'📋 Credenciales existentes: {len(creds_existentes)}')
print(f'📋 Nombres existentes: {len(nombres_existentes)}')

# Nueva estructura de equipos
equipos = {
    'MELANIE': {
        'agentes': ['mza1','mza2','mza3','mza4','mza5','mza6','mza7','mza8','mza9','mza10','mza12','mza81','mza82','mza83','mza301'],
        'supervisores': ['mza_sup4']
    },
    'YASMIN': {
        'agentes': ['mza13','mza14','mza15','mza16','mza18','mza19','mza20','mza21','mza22','mza23','mza24','mza73','mza74','mza77','mza100'],
        'supervisores': []
    },
    'JOSEFINA': {
        'agentes': ['mza25','mza26','mza27','mza28','mza29','mza30','mza31','mza32','mza33','mza75','mza76','mza80','mza302'],
        'supervisores': ['mza_sup3']
    },
    'NATALI': {
        'agentes': ['mza34','mza35','mza36','mza37','mza38','mza39','mza40','mza41','mza42','mza43','mza78','mza79'],
        'supervisores': []
    },
    'DIANA': {
        'agentes': ['mza46','mza47','mza48','mza49','mza50','mza51','mza52','mza53','mza54','mza55','mza56','mza57','mza58','mza59','mza60','mza61','mza62','mza63','mza64','mza65','mza66','mza67','mza68','mza69','mza70','mza71','mza84','mza85','mza86','mza87','mza88','mza89','mza90','mza91','mza92','mza93','mza323','mza324','mza325','mza326','mza327'],
        'supervisores': ['mza_sup2','mza_sup5']
    }
}

def get_nombre(usuario):
    u = usuario.lower().replace('_','')
    for key, val in nombres_existentes.items():
        if key.replace('_','') == u:
            return val
    for key, val in creds_existentes.items():
        if key.replace('_','') == u:
            return val.get('Nombre','').strip()
    num = usuario.replace('mza','').replace('_',' ').upper()
    return f'MZA {num}'

def gen_pass():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ===== ESCRIBIR LISTADO-DE-VENDEDORES.csv =====
empty_cols = ','.join(['""']*21)
with open('LISTADO-DE-VENDEDORES.csv', 'w', encoding='latin-1', newline='') as f:
    f.write(f'"Usuario","Nombre","Equipo",{empty_cols}\n')
    for equipo, data in equipos.items():
        for ag in data['agentes']:
            nombre = get_nombre(ag)
            f.write(f'"{ag}","{nombre}","{equipo}",{empty_cols}\n')
        for sup in data['supervisores']:
            nombre = get_nombre(sup)
            f.write(f'"{sup}","{nombre}","{equipo}",{empty_cols}\n')

total = sum(len(d['agentes'])+len(d['supervisores']) for d in equipos.values())
print(f'✅ LISTADO actualizado: {total} registros')

# ===== ESCRIBIR credenciales_eva.csv =====
with open('credenciales_eva.csv', 'w', encoding='latin-1', newline='') as f:
    f.write('Usuario,Contraseña,Nombre,Equipo,Rol\n')
    f.write('matias,mercurio,Matias,,admin\n')
    
    sup_dashboard = [
        ('diana','Qr9sVt4y','Diana','DIANA','supervisor'),
        ('calidad','Wd8fPn5z','Calidad','','supervisor'),
        ('melani','Yx3gRk7v','Melani','MELANIE','supervisor'),
        ('josefina','Nt5cWq8m','Josefina','JOSEFINA','supervisor'),
        ('yasmin','Bv2jHs6p','Yasmin','YASMIN','supervisor'),
        ('nati','Zf4dKt9r','Nati','NATALI','supervisor'),
        ('capacitacion','Mc7xJn2b','Capacitación','','supervisor'),
    ]
    for u,p,n,e,r in sup_dashboard:
        f.write(f'{u},{p},{n},{e},{r}\n')
    
    for equipo, data in equipos.items():
        for ag in data['agentes']:
            nombre = get_nombre(ag)
            cred = creds_existentes.get(ag.lower())
            pwd = cred['Contraseña'].strip() if cred and 'Contraseña' in cred else gen_pass()
            f.write(f'{ag},{pwd},{nombre},{equipo},vendedor\n')
        for sup in data['supervisores']:
            nombre = get_nombre(sup)
            u_alt = sup.replace('_','')
            cred = creds_existentes.get(sup) or creds_existentes.get(u_alt)
            pwd = cred['Contraseña'].strip() if cred and 'Contraseña' in cred else gen_pass()
            f.write(f'{sup},{pwd},{nombre},{equipo},supervisor\n')

total_creds = 1 + len(sup_dashboard) + total
print(f'✅ Credenciales actualizadas: {total_creds} registros')
print()
for eq, data in equipos.items():
    print(f'  {eq}: {len(data["agentes"])} agentes + {len(data["supervisores"])} supervisores')

# Agentes eliminados
agentes_viejos = set(creds_existentes.keys()) - {'matias','diana','calidad','melani','josefina','yasmin','nati','capacitacion','byl','marina'}
agentes_nuevos = set()
for data in equipos.values():
    for ag in data['agentes'] + data['supervisores']:
        agentes_nuevos.add(ag.lower())
eliminados = agentes_viejos - agentes_nuevos
if eliminados:
    print(f'\n🗑️ Agentes eliminados: {sorted(eliminados)}')
