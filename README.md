# Template Chatbot Streamlit com Login e Memória

Este é um template para criar aplicações de chatbot usando Streamlit, com funcionalidades integradas de login de usuário (via Google), armazenamento de histórico de conversas e dados de perfil/uso no Firebase Firestore, e integração com a API de Assistentes da OpenAI.

## Funcionalidades

*   **Autenticação de Usuário:** Login seguro via conta Google usando `st.experimental_user`.
*   **Interface de Chat:** Componente `st.chat_message` e `st.chat_input` para interação.
*   **Memória de Conversa:** Histórico de chats é salvo no Firestore e pode ser recarregado.
*   **Perfil de Usuário:** Armazena informações básicas do usuário (nome, email, foto) e permite adicionar campos personalizados (CEP, telefone, data de nascimento, instruções para o chatbot).
*   **Log de Ações:** Registra ações importantes do usuário (login, logout, criação/abertura/exclusão de chat, etc.) no Firestore.
*   **Integração OpenAI Assistants:** Utiliza a API de Assistentes da OpenAI para respostas inteligentes.
*   **Painel Administrativo:** Uma página simples protegida por senha para visualizar dados de usuários, logs e chats armazenados no Firestore.
*   **Documentação Integrada:** Uma página no aplicativo exibindo toda a documentação de uso e configuração.

## Configuração Inicial

Siga estes passos para configurar e rodar o template:

**1. Clone o Repositório:**

```bash
git clone <url_do_seu_repositorio>
cd <nome_da_pasta_do_projeto>
```

**2. Crie um Ambiente Virtual (Recomendado):**

```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

**3. Instale as Dependências:**

```bash
pip install -r requirements.txt
```

**4. Configure o Firebase:**

*   Crie um projeto no [Firebase Console](https://console.firebase.google.com/).
*   No seu projeto, vá para "Firestore Database" e crie um banco de dados no modo **Produção** (as regras de segurança podem ser ajustadas depois, se necessário). Escolha a localização do servidor mais próxima de você.
*   Vá para "Configurações do projeto" > "Contas de serviço".
*   Clique em "Gerar nova chave privada" e baixe o arquivo JSON.
*   **Para desenvolvimento local:** Renomeie o arquivo baixado para `firebase-key.json` e coloque-o na raiz do seu projeto.
*   **Para deploy no Streamlit Community Cloud:**
    *   Não inclua o `firebase-key.json` no seu repositório Git (adicione-o ao `.gitignore` se ainda não estiver).
    *   Abra o arquivo JSON da chave privada e copie os valores.
    *   No Streamlit Community Cloud, vá para as configurações do seu app e adicione os seguintes secrets:
        *   `firebase.type`: "service_account"
        *   `firebase.project_id`: "seu-project-id"
        *   `firebase.private_key_id`: "seu-private-key-id"
        *   `firebase.private_key`: "-----BEGIN PRIVATE KEY-----\nSEU_PRIVATE_KEY\n-----END PRIVATE KEY-----\n" (Copie exatamente como está no JSON, incluindo as quebras de linha `\n`)
        *   `firebase.client_email`: "seu-client-email@seu-project-id.iam.gserviceaccount.com"
        *   `firebase.client_id`: "seu-client-id"
        *   `firebase.auth_uri`: "https://accounts.google.com/o/oauth2/auth"
        *   `firebase.token_uri`: "https://oauth2.googleapis.com/token"
        *   `firebase.auth_provider_x509_cert_url`: "https://www.googleapis.com/oauth2/v1/certs"
        *   `firebase.client_x509_cert_url`: "sua-url-cert"
        *   `firebase.universe_domain`: "googleapis.com"

**5. Configure a API da OpenAI:**

*   Crie uma conta na [Plataforma OpenAI](https://platform.openai.com/).
*   Vá para a seção de API Keys e crie uma nova chave secreta.
*   Adicione a chave como um secret no Streamlit (localmente no arquivo `.streamlit/secrets.toml` ou nas configurações do app no Streamlit Community Cloud):
    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY="sk-..."
    ASSISTANT_ID="asst_..."
    ```

**6. Crie um Assistente OpenAI:**

*   Vá para a seção [Assistants](https://platform.openai.com/assistants) na plataforma OpenAI.
*   Crie um novo assistente. Defina o nome, as instruções (o prompt do sistema que define a personalidade e o objetivo do chatbot) e escolha um modelo (ex: `gpt-4o`, `gpt-4-turbo`).
*   **Importante:** Por enquanto, este template não utiliza as ferramentas nativas dos Assistentes (Code Interpreter, Retrieval, Functions). Você pode configurá-las, mas a lógica de interação no `paginas/chatbot.py` precisaria ser adaptada para usá-las.
*   Copie o ID do assistente criado (ex: `asst_...`).
*   Adicione o ID como um secret no Streamlit (localmente no arquivo `.streamlit/secrets.toml` ou nas configurações do app no Streamlit Community Cloud), como mostrado no passo anterior (`ASSISTANT_ID`).

**7. Configure a Senha do Admin:**

*   A senha padrão para o painel administrativo está definida diretamente no código em `paginas/admin.py` (procure por `if senha == 'eita':`). **É altamente recomendável alterar esta senha para algo seguro** ou implementar um método de autenticação mais robusto se o painel administrativo for crítico.

## Executando a Aplicação

Após a configuração, execute o Streamlit:

```bash
streamlit run app.py
```

A aplicação estará disponível no seu navegador local, geralmente em `http://localhost:8501`.

## Personalização

*   **Ícones e Logos:** Substitua os arquivos na pasta `arquivos/` pelos seus próprios (`logo.png`, `logo2.png`, `avatar.png`, `avatar_assistant.png`). Atualize as referências em `app.py` e `paginas/chatbot.py` se mudar os nomes dos arquivos.
*   **Textos da Interface:** Modifique os títulos, mensagens e textos diretamente nos arquivos `.py` (`app.py`, `paginas/chatbot.py`, etc.).
*   **Prompt do Assistente:** Edite as instruções do seu assistente diretamente na [Plataforma OpenAI](https://platform.openai.com/assistants). Isso mudará o comportamento e a personalidade do seu chatbot.
*   **Campos de Perfil:** Você pode adicionar/remover campos do perfil do usuário modificando:
    *   A estrutura `dados_usuario` na função `login_usuario` em `paginas/funcoes.py`.
    *   O formulário de edição e a exibição no modo visualização em `paginas/perfil.py`.
    *   A leitura desses campos no Firestore, se necessário em outras partes.
*   **Nome da Coleção Firestore:** O nome principal da coleção de usuários está definido como uma variável global `COLECAO_USUARIOS` em `paginas/funcoes.py`. Para alterar, basta mudar o valor dessa variável.

## Estrutura do Banco de Dados (Firestore)

A aplicação utiliza a seguinte estrutura no Firestore:

*   `chatbot-usuarios/` (Coleção Raiz - nome definido na variável `COLECAO_USUARIOS` em `paginas/funcoes.py`)
    *   `{user_email}/` (Documento do Usuário - ID é o email)
        *   `email`: (String) Email do usuário
        *   `nome`: (String) Nome completo
        *   `primeiro_nome`: (String) Primeiro nome
        *   `ultimo_nome`: (String) Último nome
        *   `foto`: (String) URL da foto do perfil Google
        *   `data_cadastro`: (Timestamp) Data/hora do primeiro login
        *   `ultimo_acesso`: (Timestamp) Data/hora do último acesso
        *   `cep`: (String) CEP do usuário
        *   `telefone`: (String) Telefone do usuário
        *   `instrucoes`: (String) Instruções personalizadas para o chatbot
        *   `data_nascimento`: (Timestamp) Data de nascimento
        *   `logs/` (Subcoleção)
            *   `{log_id}/` (Documento de Log)
                *   `acao`: (String) Nome da ação (ex: "Login", "Novo Chat")
                *   `detalhes`: (String/Map) Detalhes adicionais
                *   `data_hora`: (Timestamp) Data/hora da ação
        *   `chats/` (Subcoleção)
            *   `{chat_id}/` (Documento de Chat)
                *   `nome`: (String) Nome do chat (gerado a partir do primeiro prompt)
                *   `data_criacao`: (Timestamp) Data/hora de criação
                *   `ultima_atualizacao`: (Timestamp) Data/hora da última mensagem
                *   `mensagens`: (Array<Map>) Lista de mensagens
                    *   `role`: (String) "user" ou "assistant"
                    *   `content`: (String) Conteúdo da mensagem

## Arquivos Principais

*   `app.py`: Ponto de entrada da aplicação, lida com login e navegação.
*   `requirements.txt`: Dependências Python.
*   `.streamlit/secrets.toml`: Armazena chaves de API e IDs (não versionar no Git!).
*   `paginas/`: Contém os módulos de cada página da aplicação.
    *   `chatbot.py`: Lógica principal da interface do chatbot e interação com OpenAI.
    *   `perfil.py`: Exibição e edição do perfil do usuário.
    *   `admin.py`: Painel administrativo para visualização de dados.
    *   `funcoes.py`: Funções auxiliares (interação com Firebase, formatação, etc.).
    *   `documentacao.py`: Página que exibe a documentação do template.
*   `arquivos/`: Armazena arquivos estáticos (imagens, logos).
*   `firebase-key.json`: Chave de serviço do Firebase (apenas para desenvolvimento local, não versionar!). 