class Materia:
    def __init__(self, id, nombre, dictado, corr_cursada, corr_final):
        self.id = id
        self.nombre = nombre
        self.dictado = dictado 
        self.corr_cursada = corr_cursada # Lista de IDs (ej: ["ayda1"])
        self.corr_final = corr_final     # Lista de IDs para bloqueos de títulos o años
        self.peso = 0 

    def __repr__(self):
        return f"Materia({self.id})"

    def se_puede_cursar(self, progreso_usuario, cuatri_actual):
        """
        Control para anotar la materia en el calendario.
        Regla: Cursada aprobada de las anteriores habilita cursar la siguiente.
        """
        if self.dictado != 0 and self.dictado != cuatri_actual:
            return False

        if progreso_usuario.get(self.id, {}).get('cursada', False):
            return False

        # Para CURSAR, pedimos que las correlativas de cursada estén al menos 'cursadas'
        for c_id in self.corr_cursada:
            if not progreso_usuario.get(c_id, {}).get('cursada', False):
                return False

        # Si el plan pide finales para cursar (bloqueos de año), chequeamos corr_final
        for f_id in self.corr_final:
            if not progreso_usuario.get(f_id, {}).get('final', False):
                return False

        return True

    def se_puede_rendir_final(self, progreso_usuario):
        """
        Control para habilitar el examen final.
        NUEVA REGLA: Para rendir el final de esta, las que habilitaron su cursada 
        deben tener el FINAL aprobado.
        """
        estado_materia = progreso_usuario.get(self.id, {})

        if estado_materia.get('final', False):
            return "APROBADO"

        if not estado_materia.get('cursada', False):
            return "BLOQUEADO_CURSADA"

        # --- EL CAMBIO ESTÁ ACÁ ---
        # Chequeamos que las correlativas de cursada ya tengan su FINAL hecho
        for c_id in self.corr_cursada:
            if not progreso_usuario.get(c_id, {}).get('final', False):
                return "BLOQUEADO_FINAL_PREVIO"
        
        # También chequeamos si hay correlativas de final específicas adicionales
        for f_id in self.corr_final:
            if not progreso_usuario.get(f_id, {}).get('final', False):
                return "BLOQUEADO_FINAL_PREVIO"

        return "LISTO"