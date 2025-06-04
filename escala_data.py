class EscalaData:
    def __init__(self, vagas, reservas):
        self.vagas = vagas  # Vagas principais
        self.reservas = reservas  # Vagas de reserva
        self.principais = []  # Lista de participantes principais
        self.reservas_list = []  # Lista de reservas

    def inscrever(self, usuario, tipo):
        if tipo == "principal":
            if len(self.principais) < self.vagas:
                self.principais.append(usuario)
                return f"{usuario} inscrito como principal!"
            else:
                return "Não há vagas principais disponíveis."
        elif tipo == "reserva":
            if len(self.reservas_list) < self.reservas:
                self.reservas_list.append(usuario)
                return f"{usuario} inscrito como reserva!"
            else:
                return "Não há vagas de reserva disponíveis."
        return "Tipo inválido de inscrição."

    def cancelar_inscricao(self, usuario, tipo):
        """Método para cancelar inscrição de um participante"""
        if tipo == "principal":
            if usuario in self.principais:
                self.principais.remove(usuario)
                return f"{usuario} removido das vagas principais."
            else:
                return f"{usuario} não está inscrito como principal."
        elif tipo == "reserva":
            if usuario in self.reservas_list:
                self.reservas_list.remove(usuario)
                return f"{usuario} removido das vagas de reserva."
            else:
                return f"{usuario} não está inscrito como reserva."
        return "Tipo inválido de inscrição."

    def get_participantes(self):
        return self.principais

    def get_reservas(self):
        return self.reservas_list

    def get_vagas_restantes(self):
        # Considera tanto vagas principais quanto de reservas
        vagas_restantes = self.vagas - len(self.principais)
        return vagas_restantes if vagas_restantes > 0 else 0

    def get_reservas_restantes(self):
        # Calcula as reservas restantes
        reservas_restantes = self.reservas - len(self.reservas_list)
        return reservas_restantes if reservas_restantes > 0 else 0
