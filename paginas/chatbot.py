import streamlit as st
from openai import OpenAI 
from paginas.funcoes import obter_perfil_usuario, registrar_acao_usuario, salvar_chat, obter_chats, obter_chat, excluir_chat
from paginas.funcoes import login_usuario, inicializar_firebase
from datetime import datetime

 
# Inicializa o Firebase
inicializar_firebase() 

# Verifica se o usuário está logado
if not hasattr(st.experimental_user, 'is_logged_in') or not st.experimental_user.is_logged_in:
    st.warning("Você precisa fazer login para acessar o chatbot.")
    st.stop()

# Realiza o login do usuário (atualiza último acesso)
login_usuario() 

# Registra a ação de login apenas na primeira vez que a página é carregada na sessão
if 'login_registrado' not in st.session_state:
    registrar_acao_usuario("Login", "Página Inicial")
    st.session_state['login_registrado'] = True

# Obtém o perfil e define o nome do usuário ANTES de usar no popover
perfil = obter_perfil_usuario()
# Usa o primeiro nome para a saudação, com fallback para o given_name do login ou 'Usuário'
nome_usuario = perfil.get("primeiro_nome", getattr(st.experimental_user, 'given_name', 'Usuário'))

# Verifica e exibe a mensagem de boas-vindas no primeiro login
if st.session_state.get('show_welcome_message', False):
    with st.popover("Bem-vindo(a)! 🎉", use_container_width=True):
        st.markdown(f"Olá, **{nome_usuario}**! Ficamos felizes em ter você por aqui.")
        st.markdown("Explore o chatbot e personalize sua experiência na página **Meu Perfil**.")
        st.button("Entendi!", use_container_width=True, key="welcome_close")
    # Remove o flag para não mostrar novamente
    del st.session_state['show_welcome_message']

# Configurações iniciais
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Define o avatar do usuário: usa a foto do perfil se for uma URL válida, senão usa o avatar padrão
user_picture = getattr(st.experimental_user, 'picture', None)
if user_picture and isinstance(user_picture, str) and user_picture.startswith(('http://', 'https://')):
    avatar_user = user_picture
else:
    avatar_user = 'arquivos/avatar_usuario.png'

# Define o avatar do assistente
avatar_assistant = 'arquivos/avatar_assistente.png'
MENSAGEM_INICIAL = 'Olá! Como posso te ajudar hoje?' # Mensagem inicial genérica

# Inicialização do histórico de mensagens e chat ativo
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": MENSAGEM_INICIAL # Avatar não é mais armazenado na mensagem
        }
    ]

if 'chat_ativo_id' not in st.session_state:
    st.session_state.chat_ativo_id = None

if 'chat_ativo_nome' not in st.session_state:
    st.session_state.chat_ativo_nome = "Novo Chat"

# Sidebar com histórico de chats
with st.sidebar:
    st.html(f"""
        <div style="text-align: left; margin: 10px 0">
            <h1 style="font-size: 2.0em">
                <span style="
                    background: linear-gradient(45deg, #003366, #3399FF); /* Azul escuro para azul normal */
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-weight: bold;
                ">
                    Olá, {nome_usuario}!
                </span>
            </h1>
        </div>
        """) 
    
    # Botão de novo chat
    if st.button("✨ Novo Chat", key="novo_chat", use_container_width=True, type="primary"):
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": MENSAGEM_INICIAL # Avatar não é mais armazenado na mensagem
            }
        ]
        st.session_state.chat_ativo_id = None
        st.session_state.chat_ativo_nome = "Novo Chat"
        registrar_acao_usuario("Novo Chat", "Usuário iniciou um novo chat")
        st.rerun()
    
    # Exibir chats existentes
    chats = obter_chats()
    st.write("---")
    st.write("📜 **Chats Anteriores**")
    
    # CSS personalizado para alinhar botões à esquerda
    st.markdown("""
        <style>
        /* Estiliza os botões de chat anterior usando o prefixo da chave */
        [class*="st-key-chat_"] button {
            text-align: left !important;
            justify-content: flex-start !important;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Inicia uma div com uma classe específica para os botões de chat
    st.markdown('<div class="chat-button-section">', unsafe_allow_html=True)
    
    if len(chats) == 0:
        st.info("Você ainda não tem conversas salvas!")
    
    for chat in chats:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{chat['nome']}", key=f"chat_{chat['id']}", use_container_width=True):
                chat_data = obter_chat(chat['id'])
                if chat_data and 'mensagens' in chat_data:
                    st.session_state.mensagens = chat_data['mensagens']
                    st.session_state.chat_ativo_id = chat['id']
                    st.session_state.chat_ativo_nome = chat['nome']
                    registrar_acao_usuario("Abrir Chat", f"Usuário abriu o chat {chat['nome']}")
                    st.rerun()
        with col2:
            if st.button("🗑️", key=f"excluir_{chat['id']}"):
                excluir_chat(chat['id'])
                registrar_acao_usuario("Excluir Chat", f"Usuário excluiu o chat {chat['nome']}")
                # Se o chat excluído for o ativo, iniciar um novo chat
                if st.session_state.chat_ativo_id == chat['id']:
                    st.session_state.mensagens = [
                        {
                            "role": "assistant",
                            "content": MENSAGEM_INICIAL # Avatar não é mais armazenado na mensagem
                        }
                    ]
                    st.session_state.chat_ativo_id = None
                    st.session_state.chat_ativo_nome = "Novo Chat"
                st.rerun()
    
    # Fecha a div
    st.markdown('</div>', unsafe_allow_html=True)
 

# Exibição do histórico de mensagens
for mensagem in st.session_state.mensagens:
    role = mensagem["role"]
    # Define o avatar a ser exibido baseado no role, usando as variáveis globais corretas,
    # ignorando o valor 'avatar' potencialmente incorreto salvo na mensagem.
    if role == "user":
        display_avatar = avatar_user
    elif role == "assistant":
        display_avatar = avatar_assistant
    else:
        display_avatar = None # Caso haja algum outro role inesperado
        
    with st.chat_message(role, avatar=display_avatar):
        st.write(mensagem["content"])

# Input e processamento de mensagens
prompt = st.chat_input()

if prompt:
    # Adiciona mensagem do usuário
    st.session_state.mensagens.append({
        "role": "user",
        "content": prompt
        # Avatar não é mais armazenado na mensagem
    })
    
    # Mostra mensagem do usuário
    with st.chat_message("user", avatar=avatar_user):
        st.write(prompt)

    # Processa resposta do assistente
    with st.chat_message("assistant", avatar=avatar_assistant):
        try: # Adiciona try para capturar erros da API OpenAI
            # Prepara mensagens para a thread
            messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.mensagens
                if msg["role"] in ["user", "assistant"]
            ]
            
            # Cria e processa a thread
            thread = client.beta.threads.create(messages=messages)
            
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=st.secrets["ASSISTENTE"] # Usa um único ID de assistente definido nos secrets
            ) as stream:
                assistant_reply = ""
                message_placeholder = st.empty()
                
                for event in stream:
                    if event.event == 'thread.message.delta':
                        delta = event.data.delta.content[0].text.value
                        assistant_reply += delta
                        message_placeholder.markdown(assistant_reply)
                        #time.sleep(0.01)
                
                # Adiciona resposta ao histórico
                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content": assistant_reply
                })
                
                # Log e salvamento do chat
                registrar_acao_usuario("Conversa com Chatbot", {'prompt': prompt, 'resposta': assistant_reply})
                
                # Salva o chat automaticamente
                if len(st.session_state.mensagens) > 2:  # Se houver mais que a mensagem inicial e uma resposta
                    # Extrair o primeiro prompt do usuário para usar como nome do chat
                    primeiro_prompt = next((msg["content"] for msg in st.session_state.mensagens if msg["role"] == "user"), None)
                    
                    # --- Sugestão 4: Gerar nome do chat com LLM --- 
                    nome_chat_sugerido = None
                    if primeiro_prompt:
                        try:
                            # Chama a API de chat completion para gerar um título curto
                            response_titulo = client.chat.completions.create(
                                model="gpt-4o-mini", # Ou outro modelo eficiente
                                messages=[
                                    {"role": "system", "content": "Você é um assistente que cria títulos curtos (máximo 5 palavras) para conversas de chat, baseado no primeiro prompt do usuário."},
                                    {"role": "user", "content": f"Crie um título curto para uma conversa que começa com: '{primeiro_prompt}'"}
                                ],
                                temperature=0.5
                            )
                            nome_chat_sugerido = response_titulo.choices[0].message.content.strip().replace('\"' ,'')
                        except Exception as e:
                            print(f"Erro ao gerar título do chat com LLM: {e}")
                            # Fallback para o nome baseado no prompt
                            nome_chat_sugerido = primeiro_prompt[:25] + "..." if len(primeiro_prompt) > 25 else primeiro_prompt
                    else:
                         # Fallback se não houver primeiro prompt (improvável aqui, mas seguro)
                         nome_chat_sugerido = f"Chat {datetime.now().strftime('%H:%M')}"
                    # --- Fim Sugestão 4 ---
                    
                    # Usa o nome sugerido ou o nome ativo se já existir um
                    nome_chat_final = nome_chat_sugerido if st.session_state.chat_ativo_id is None else st.session_state.chat_ativo_nome
                    
                    chat_id = salvar_chat(nome_chat_final, st.session_state.mensagens)
                    if chat_id: # Só atualiza o estado se o chat foi salvo com sucesso
                        st.session_state.chat_ativo_id = chat_id
                        st.session_state.chat_ativo_nome = nome_chat_final

        # Trata erros específicos da API OpenAI (agora com indentação correta)
        except Exception as e:
             print(f"Erro na chamada OpenAI: {e}")
             st.error(f"Ocorreu um erro ao comunicar com o assistente: {e}. Tente novamente.")
             # Remove a última mensagem (resposta com erro) do histórico para não poluir
             if st.session_state.mensagens and st.session_state.mensagens[-1]["role"] == "assistant":
                 st.session_state.mensagens.pop()


# Informações do usuário na barra lateral
with st.sidebar:  
    if hasattr(st.experimental_user, 'is_logged_in') and st.experimental_user.is_logged_in:
        st.divider()
        
        # Exibir apenas o e-mail do usuário
        if hasattr(st.experimental_user, 'email'):
            st.html(f'<p style="font-size:10px; color:#666; margin-bottom:0px;"><strong>Usuário: </strong>{st.experimental_user.email}</p>')
        
        st.page_link("paginas/perfil.py", label="Meu Perfil", icon="👨‍💼", use_container_width=True)
        
        st.page_link("paginas/termos.py", label="Termos e Privacidade", icon="📄", use_container_width=True)
        
        st.html(f'<p style="font-size:10px; color:#666; margin-bottom:0px;">Área Administrativa</p>')
     
        st.page_link("paginas/documentacao.py", label="Documentação", icon="📚", use_container_width=True)

        st.page_link("paginas/admin.py", label="Acessar base de dados", icon="🎲", use_container_width=True)
        
        # Botão de logout
        if st.button("Logout", 
                     key="logout_button", 
                     type='secondary', 
                     icon=':material/logout:',
                     use_container_width=True):
            registrar_acao_usuario("Logout", "Usuário fez logout do sistema")
            st.logout()
