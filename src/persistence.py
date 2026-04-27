import json
import os
from src.models import Materia 

def cargar_plan(nombre_plan):
    """Lee el JSON de la carrera y devuelve objetos Materia."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Cambiamos a 'carreras' porque así tenés tu carpeta
    ruta = os.path.join(base_path, 'data', 'carreras', f'{nombre_plan}.json')
    
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el plan en: {ruta}")

    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    lista_materias = []
    for m in datos['materias']:
        obj = Materia(
            id=m['id'],
            nombre=m['nombre'],
            dictado=m['dictado'],
            corr_cursada=m.get('correlativas_cursada', []),
            corr_final=m.get('correlativas_final', [])
        )
        lista_materias.append(obj)
    
    return lista_materias, datos['carrera']

def cargar_progreso_usuario(nombre_usuario):
    """Busca el archivo JSON del usuario y devuelve su progreso."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nombre_archivo = f"{nombre_usuario.lower()}.json"
    ruta = os.path.join(base_path, 'data', 'usuarios', nombre_archivo)
    
    if not os.path.exists(ruta):
        return {} 
    
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    return datos.get('progreso', {})

def guardar_progreso_usuario(nombre_usuario, progreso, plan_id):
    """Guarda el progreso del usuario en un archivo JSON."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nombre_archivo = f"{nombre_usuario.lower()}.json"
    ruta = os.path.join(base_path, 'data', 'usuarios', nombre_archivo)
    
    datos = {
        "nombre": nombre_usuario,
        "plan": plan_id,
        "progreso": progreso
    }
    
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)