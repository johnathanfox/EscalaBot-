# Bot de Gerenciamento de Escalações para Discord

> ⚠️ **Projeto Privado** - Este repositório contém código proprietário e confidencial.

Um bot de Discord para gerenciar escalações de times, permitindo a criação de eventos, inscrições em vagas principais e reservas.

## 📋 Funcionalidades

- Criação de eventos de escalação com vagas limitadas
- Sistema de vagas principais e reservas
- Inscrição/desistência com apenas um clique
- Exibição clara de participantes confirmados e reservas
- Interface intuitiva com botões interativos
- Suporte a imagens personalizadas nos eventos

## 🚀 Como Usar

1. **Configuração Inicial**
   - Crie um bot no [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
   - Adicione o bot ao seu servidor com as permissões necessárias
   - Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
     ```
     DISCORD_TOKEN=seu_token_aqui
     ```

2. **Instalação**
   ```bash
   # Clone o repositório
   git clone https://github.com/seu-usuario/escalation-bot-discord.git
   cd escalation-bot-discord
   
   # Crie um ambiente virtual (opcional, mas recomendado)
   python -m venv .venv
   .venv\Scripts\activate  # No Windows
   
   # Instale as dependências
   pip install -r requirements.txt
   ```

3. **Executando o Bot**
   ```bash
   python bot.py
   ```

4. **Comandos**
   - `/criar_escalacao`: Cria um novo evento de escalação

## 🛠️ Estrutura do Projeto

- `bot.py`: Ponto de entrada principal do bot
- `views.py`: Implementação das interfaces de usuário (modais e botões)
- `escala_data.py`: Lógica de negócio para gerenciamento das escalações
- `requirements.txt`: Dependências do projeto

## 🤝 Uso e Distribuição

Este é um projeto privado e confidencial. Qualquer uso, cópia, modificação ou distribuição não autorizada é estritamente proibida.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato com os mantenedores.
