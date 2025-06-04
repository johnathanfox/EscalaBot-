import discord
from discord.ui import Modal, TextInput, View, Button
import re

class EscalaData:
    def __init__(self, vagas, reservas):
        self.vagas = vagas
        self.reservas = reservas
        self.principais = []
        self.reservas_lista = []

    def esta_inscrito(self, usuario):
        return (usuario in self.principais, usuario in self.reservas_lista)

    def remover_inscricao(self, usuario):
        if usuario in self.principais:
            self.principais.remove(usuario)
            return True, "principal"
        elif usuario in self.reservas_lista:
            self.reservas_lista.remove(usuario)
            return True, "reserva"
        return False, None

    def inscrever(self, usuario, tipo):
        # Primeiro verifica se já está inscrito
        inscrito_principal, inscrito_reserva = self.esta_inscrito(usuario)
        
        # Se já está inscrito no tipo solicitado, retorna erro
        if (tipo == "principal" and inscrito_principal) or (tipo == "reserva" and inscrito_reserva):
            return False, "Você já está inscrito nesta categoria!"

        if tipo == "principal":
            # Se já está na reserva, remove da reserva primeiro
            if inscrito_reserva:
                self.reservas_lista.remove(usuario)

            if len(self.principais) < self.vagas:
                self.principais.append(usuario)
                return True, "principal"
            else:
                # Se não conseguiu entrar como principal, tenta como reserva
                if len(self.reservas_lista) < self.reservas:
                    self.reservas_lista.append(usuario)
                    return True, "reserva"
                else:
                    return False, "Não há vagas disponíveis!"

        elif tipo == "reserva":
            # Não permite se já está como principal
            if inscrito_principal:
                return False, "Você já está inscrito como participante principal!"

            if len(self.reservas_lista) < self.reservas:
                self.reservas_lista.append(usuario)
                return True, "reserva"
            else:
                return False, "Não há vagas para reserva disponíveis!"

    def get_participantes_text(self):
        if not self.principais:
            return "(ninguém ainda confirmado)"
        return "\n".join([f"✅ {p.mention}" for p in self.principais])

    def get_reservas_text(self):
        if not self.reservas_lista:
            return "(ninguém ainda como reserva)"
        return "\n".join([f"🕗 {r.mention}" for r in self.reservas_lista])

    def get_vagas_restantes(self):
        return self.vagas - len(self.principais)

# Modal único com todos os campos
class CriarEscalacaoModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Criar Escalação")

        self.nome = TextInput(
            label="Nome e Imagem",
            placeholder="Nome: Operação Fênix\nImagem (opcional): https://exemplo.com/imagem.png",
            style=discord.TextStyle.paragraph
        )
        self.data = TextInput(label="Data", placeholder="Ex: 25/04/2025", style=discord.TextStyle.short)
        self.hora = TextInput(
            label="Horários",
            placeholder="Hora: 20:30\nPreparação: 20:00",
            style=discord.TextStyle.paragraph
        )
        self.vagas = TextInput(label="Vagas principais", placeholder="Ex: 5", style=discord.TextStyle.short)
        self.reservas = TextInput(label="Reservas", placeholder="Ex: 2", style=discord.TextStyle.short)

        for item in [self.nome, self.data, self.hora, self.vagas, self.reservas]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        # Processar nome e imagem
        nome_imagem = [linha.strip() for linha in self.nome.value.split('\n') if linha.strip()]
        print(f"Linhas do campo nome/imagem: {nome_imagem}")
        
        # Processar nome
        nome = nome_imagem[0]
        if 'nome:' in nome.lower():
            nome = nome.split(':', 1)[1].strip()
        print(f"Nome processado: {nome}")
        
        # Processar imagem
        imagem_link = None
        if len(nome_imagem) > 1:
            imagem_texto = nome_imagem[1].lower()
            print(f"Texto da imagem: {imagem_texto}")
            
            # Se começa com http ou https, usa direto
            if imagem_texto.startswith('http://') or imagem_texto.startswith('https://'):
                imagem_link = imagem_texto
            # Se tem 'imagem:', remove o prefixo
            elif 'imagem:' in imagem_texto:
                imagem_link = imagem_texto.split(':', 1)[1].strip()
            
            if imagem_link:
                print(f"Link da imagem encontrado: {imagem_link}")
                # Verifica se é uma URL válida
                if not imagem_link.startswith(('http://', 'https://')):
                    await interaction.response.send_message(
                        "Erro: O link da imagem deve começar com http:// ou https://", 
                        ephemeral=True
                    )
                    return
                
                # Remove query parameters (tudo depois do ?) para verificar a extensão
                url_base = imagem_link.split('?')[0]
                print(f"URL base para verificação: {url_base}")
                
                # Verifica se é uma URL do Discord ou uma imagem normal
                if not (url_base.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) or 
                        'cdn.discordapp.com/attachments' in url_base):
                    await interaction.response.send_message(
                        "Erro: O link deve ser uma imagem (.jpg, .jpeg, .png, .gif, .webp) ou um link do Discord.", 
                        ephemeral=True
                    )
                    return

        # Validar data
        if not re.match(r"\d{2}/\d{2}/\d{4}", self.data.value):
            await interaction.response.send_message("Erro: A data deve estar no formato dd/mm/aaaa.", ephemeral=True)
            return

        # Processar horários
        horarios = [h.strip() for h in self.hora.value.split('\n') if h.strip()]
        print(f"Horários recebidos: {horarios}")
        
        hora_evento = None
        hora_prep = None

        for h in horarios:
            h_lower = h.lower()
            print(f"Processando horário: {h_lower}")
            
            if 'hora:' in h_lower:
                hora_evento = h_lower.replace('hora:', '').strip()
                print(f"Hora do evento encontrada: {hora_evento}")
            elif 'preparação:' in h_lower:
                hora_prep = h_lower.replace('preparação:', '').strip()
                print(f"Hora de preparação encontrada: {hora_prep}")

        # Se não encontrou o formato hora: mas tem exatamente dois horários
        if not hora_evento and len(horarios) == 2:
            # Assume que o primeiro é a hora do evento
            hora_evento = horarios[0].strip()
            hora_prep = horarios[1].strip()
            print(f"Usando formato alternativo - Evento: {hora_evento}, Prep: {hora_prep}")

        if not hora_evento:
            await interaction.response.send_message(
                "Erro: Informe a hora do evento no formato 'Hora: 20:30' ou simplesmente '20:30'.", 
                ephemeral=True
            )
            return

        # Limpar possíveis textos extras e verificar formato
        hora_evento = re.search(r'\d{2}:\d{2}', hora_evento)
        if not hora_evento:
            await interaction.response.send_message(
                "Erro: A hora do evento deve conter um horário no formato hh:mm (exemplo: 20:30).", 
                ephemeral=True
            )
            return
        hora_evento = hora_evento.group(0)

        if hora_prep:
            hora_prep = re.search(r'\d{2}:\d{2}', hora_prep)
            if not hora_prep:
                await interaction.response.send_message(
                    "Erro: A hora de preparação deve conter um horário no formato hh:mm (exemplo: 20:00).", 
                    ephemeral=True
                )
                return
            hora_prep = hora_prep.group(0)

        try:
            vagas = int(self.vagas.value)
            reservas = int(self.reservas.value)
        except ValueError:
            await interaction.response.send_message("Erro: Vagas e reservas devem ser números.", ephemeral=True)
            return

        # Cria o embed com uma cor azul vibrante
        embed = discord.Embed(color=0x3498db)  # Azul bonito
        
        # Título mais elegante
        embed.title = f"🎮 {nome}"
        
        # Adiciona a imagem logo após criar o embed
        if imagem_link:
            print(f"Configurando imagem do embed: {imagem_link}")
            embed.set_image(url=imagem_link)

        # Primeira linha: Data e Horários
        horarios_texto = f"`⏰ {hora_evento}`"
        if hora_prep:
            horarios_texto += f" (⏳ Prep: `{hora_prep}`)"
        embed.add_field(
            name="📅 Data e Horário",
            value=f"`{self.data.value}` • {horarios_texto}",
            inline=False
        )
        
        # Segunda linha: Informações de vagas
        info_vagas = f"✅ **{vagas}** vagas principais • 🕗 **{reservas}** reservas"
        embed.add_field(
            name="🎯 Informações",
            value=info_vagas,
            inline=False
        )
        
        # Terceira linha: Participantes
        embed.add_field(
            name="✅ Participantes Confirmados",
            value="​\n(ninguém ainda confirmado)",
            inline=False
        )
        
        # Quarta linha: Reservas
        embed.add_field(
            name="🕗 Lista de Reservas",
            value="​\n(ninguém ainda como reserva)",
            inline=False
        )
        
        # Rodapé com vagas restantes
        vagas_texto = f"Vagas restantes: **{vagas}**"
        embed.set_footer(text=vagas_texto)

        view = EscalaView(vagas, reservas, embed)
        await interaction.response.send_message(embed=embed, view=view)

# View com botões para inscrição nas vagas e reservas
class EscalaView(View):
    def __init__(self, vagas, reservas, embed_original):
        super().__init__(timeout=None)  # Sem timeout para os botões nunca expirarem
        self.vagas = vagas
        self.reservas = reservas
        self.embed_original = embed_original
        
        # Inicializa o objeto de inscrições
        self.inscricoes = EscalaData(vagas, reservas)

        # Adiciona os botões
        for botao in self.criar_botoes():
            self.add_item(botao)

    def criar_botoes(self):
        """Cria os botões com tamanhos fixos usando espaços Unicode"""
        # Espaço em branco especial para padding
        pad = "\u2000" * 2  # Espaço em branco largo
        
        # Botão de Participar - Verde com emoji e estilo moderno
        botao_participar = Button(
            style=discord.ButtonStyle.green,
            label=f"✅{pad}Participar{pad}✅",
            custom_id="participar"
        )
        
        # Botão de Reserva - Azul com emoji
        botao_reserva = Button(
            style=discord.ButtonStyle.primary,
            label=f"🕗{pad}Reserva{pad}🕗",
            custom_id="reserva"
        )
        
        # Botão de Sair - Vermelho discreto
        botao_sair = Button(
            style=discord.ButtonStyle.red,
            label=f"❌{pad}Remover{pad}❌",
            custom_id="sair"
        )

        # Configura os callbacks
        botao_participar.callback = self.inscrever_principal
        botao_reserva.callback = self.inscrever_reserva
        botao_sair.callback = self.remover_inscricao

        return [botao_participar, botao_reserva, botao_sair]

    async def atualizar_embed(self):
        # Atualiza os campos do embed
        self.embed_original.set_field_at(
            2,  # Índice do campo de participantes
            name="✅ Participantes Confirmados",
            value="​\n" + self.inscricoes.get_participantes_text(),
            inline=False
        )
        self.embed_original.set_field_at(
            3,  # Índice do campo de reservas
            name="🕗 Lista de Reservas",
            value="​\n" + self.inscricoes.get_reservas_text(),
            inline=False
        )

        # Atualiza o rodapé com vagas restantes
        vagas_restantes = self.inscricoes.get_vagas_restantes()
        self.embed_original.set_footer(text=f"Vagas restantes: **{vagas_restantes}**")

    async def inscrever_principal(self, interaction: discord.Interaction):
        try:
            # Primeiro responde à interação para evitar timeout
            await interaction.response.defer()
            
            sucesso, tipo = self.inscricoes.inscrever(interaction.user, "principal")
            if sucesso:
                await self.atualizar_embed()
                # Cria uma nova view com botões proporcionais
                nova_view = EscalaView(self.vagas, self.reservas, self.embed_original)
                nova_view.inscricoes = self.inscricoes  # Preserva os dados de inscrições
                try:
                    await interaction.edit_original_response(embed=self.embed_original, view=nova_view)
                    if tipo == "movido":
                        await interaction.followup.send(
                            "Você foi movido da lista de reservas para a lista principal!",
                            ephemeral=True
                        )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    # Se falhar ao editar a mensagem, ignoramos
                    pass
            else:
                try:
                    await interaction.followup.send(
                        "Você já está inscrito na lista principal!",
                        ephemeral=True
                    )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    pass
        except (discord.errors.NotFound, discord.errors.HTTPException):
            # Se a interação expirou ou falhou, ignoramos
            pass

    async def inscrever_reserva(self, interaction: discord.Interaction):
        try:
            # Primeiro responde à interação para evitar timeout
            await interaction.response.defer()
            
            sucesso, tipo = self.inscricoes.inscrever(interaction.user, "reserva")
            if sucesso:
                await self.atualizar_embed()
                # Cria uma nova view com botões proporcionais
                nova_view = EscalaView(self.vagas, self.reservas, self.embed_original)
                nova_view.inscricoes = self.inscricoes  # Preserva os dados de inscrições
                try:
                    await interaction.edit_original_response(embed=self.embed_original, view=nova_view)
                    await interaction.followup.send(
                        f"Você foi inscrito como reserva!",
                        ephemeral=True
                    )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    # Se falhar ao editar a mensagem, ignoramos
                    pass
            else:
                try:
                    await interaction.followup.send(
                        "Você já está inscrito na lista de reservas!",
                        ephemeral=True
                    )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    pass
        except (discord.errors.NotFound, discord.errors.HTTPException):
            # Se a interação expirou ou falhou, ignoramos
            pass

    async def remover_inscricao(self, interaction: discord.Interaction):
        try:
            # Primeiro responde à interação para evitar timeout
            await interaction.response.defer()
            
            sucesso, tipo = self.inscricoes.remover_inscricao(interaction.user)
            if sucesso:
                await self.atualizar_embed()
                # Cria uma nova view com botões proporcionais
                nova_view = EscalaView(self.vagas, self.reservas, self.embed_original)
                nova_view.inscricoes = self.inscricoes  # Preserva os dados de inscrições
                try:
                    await interaction.edit_original_response(embed=self.embed_original, view=nova_view)
                    await interaction.followup.send(
                        f"Você foi removido da lista {'principal' if tipo == 'principal' else 'de reservas'}!",
                        ephemeral=True
                    )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    # Se falhar ao editar a mensagem, ignoramos
                    pass
            else:
                try:
                    await interaction.followup.send(
                        "Você não está inscrito em nenhuma lista!",
                        ephemeral=True
                    )
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    pass
        except (discord.errors.NotFound, discord.errors.HTTPException):
            # Se a interação expirou ou falhou, ignoramos
            pass
