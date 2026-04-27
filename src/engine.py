import networkx as nx  

class Engine:
    def __init__(self, lista_materias):
        self.materias = {m.id: m for m in lista_materias}
        
        self.grafo = nx.DiGraph()

        self._construir_grafo()
        self._calcular_pesos()

    def _construir_grafo(self):

        for m in self.materias.values():
            # Agregamos cada materia como un punto (nodo) en el mapa
            self.grafo.add_node(m.id)
            
            # Recorremos sus correlativas de cursada
            for corr_id in m.corr_cursada:
                # Si la correlativa existe en nuestro plan...
                if corr_id in self.materias:
                    # Dibujamos una flecha que va desde la correlativa hacia la materia actual
                    # Esto indica que para llegar a 'm.id' primero hay que pasar por 'corr_id'
                    self.grafo.add_edge(corr_id, m.id)

    def _calcular_pesos(self):
        """Calcula qué tan importante es una materia basándose en cuántas destraba."""
        for m_id in self.materias:
            # 'descendants' busca todas las materias que están "colgadas" de esta, 
            # ya sea directa o indirectamente.
            descendientes = nx.descendants(self.grafo, m_id)
            
            # Le asignamos el peso: cuantas más materias destrabe, más peso tiene.
            # Ejemplo: Si de Algebra cuelgan 10 materias, su peso es 10.
            self.materias[m_id].peso = len(descendientes)

    def simular(self, progreso_inicial, max_materias, año_inicio, cuatri_inicio):
        """El motor que hace avanzar el tiempo y elige qué cursar."""
        
        # Creamos una copia del progreso actual para no arruinar los datos originales
        progreso = progreso_inicial.copy()
        
        # Identificamos qué materias faltan (las que NO están marcadas como cursadas en el progreso)
        materias_pendientes = [m for m in self.materias.values() if not progreso.get(m.id, {}).get('cursada', False)]
        
        planificacion = {}  # Diccionario donde guardaremos el resultado final
        año = año_inicio    # El año en el que empezamos
        cuatri = cuatri_inicio # El cuatrimestre (1 o 2)

        # Bucle principal: Mientras queden materias por hacer...
        while materias_pendientes:
            # Creamos una etiqueta de texto para el periodo actual (Ej: "2026 - 1° Cuatri")
            periodo_label = f"{año} - {cuatri}° Cuatri"
            
            # 1. FILTRAR: Buscamos qué materias de las pendientes se pueden cursar hoy
            # Usamos la función 'se_puede_cursar' que definimos en models.py
            disponibles = [m for m in materias_pendientes if m.se_puede_cursar(progreso, cuatri)]
            
            # 2. PRIORIZAR: Ordenamos las disponibles de MAYOR a MENOR peso estratégico
            disponibles.sort(key=lambda x: x.peso, reverse=True)
            
            # 3. LIMITAR: Tomamos solo la cantidad máxima que el usuario puede hacer (ej: las primeras 4)
            elegidas = disponibles[:max_materias]
            
            if elegidas:
                # Guardamos los nombres de las elegidas en nuestro calendario
                planificacion[periodo_label] = [m.nombre for m in elegidas]
                
                # Actualizamos el estado para el "futuro":
                for m in elegidas:
                    if m.id not in progreso: progreso[m.id] = {}
                    progreso[m.id]['cursada'] = True # La marcamos como hecha
                    materias_pendientes.remove(m)    # La sacamos de la lista de espera
            else:
                # Si no hay nada que se pueda cursar este cuatri (bloqueo), avisamos
                planificacion[periodo_label] = ["(Sin materias disponibles para cursar)"]

            # 4. AVANZAR EL RELOJ:
            if cuatri == 1:
                cuatri = 2 # Si estábamos en el 1ero, pasamos al 2do
            else:
                cuatri = 1 # Si estábamos en el 2do, pasamos al 1ero del año siguiente
                año += 1
            
            # SEGURIDAD: Si pasan más de 15 años, algo salió mal (bucle infinito) y cortamos.
            if año > año_inicio + 15: break 

        return planificacion # Devolvemos todo el calendario armado