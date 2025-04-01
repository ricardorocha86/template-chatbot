import pandas as pd
from datetime import datetime
import streamlit as st
from firebase_admin import firestore, credentials 
import firebase_admin

# Nome da coleção principal de usuários definida como variável global
COLECAO_USUARIOS = "chatbot-usuarios"

def inicializar_firebase():
    # Verifica se estamos em produção (Streamlit Cloud) ou desenvolvimento local
    if 'firebase' in st.secrets:
        cred = credentials.Certificate({
            "type": st.secrets.firebase.type,
            "project_id": st.secrets.firebase.project_id,
            "private_key_id": st.secrets.firebase.private_key_id,
            "private_key": st.secrets.firebase.private_key,
            "client_email": st.secrets.firebase.client_email,
            "client_id": st.secrets.firebase.client_id,
            "auth_uri": st.secrets.firebase.auth_uri,
            "token_uri": st.secrets.firebase.token_uri,
            "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
            "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url,
            "universe_domain": st.secrets.firebase.universe_domain
        })
    else:
        # Usa o arquivo local em desenvolvimento
        cred = credentials.Certificate("firebase-key.json")
        
    # Inicializa o Firebase apenas se ainda não foi inicializado
    try:
        firebase_admin.get_app() 
    except ValueError:
        firebase_admin.initialize_app(cred)

def login_usuario():
    """
    Registra ou atualiza dados do usuário no Firestore.
    Cria um novo registro se o usuário não existir, ou atualiza o último acesso se já existir.
    """
    if not hasattr(st.experimental_user, 'email'):
        return  # Se não houver email, não tenta registrar o usuário
        
    db = firestore.client()
    doc_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email)

    dados_usuario = {
        "email": st.experimental_user.email,
        "nome": getattr(st.experimental_user, 'name', ''),
        "primeiro_nome": getattr(st.experimental_user, 'given_name', ''),
        "ultimo_nome": getattr(st.experimental_user, 'family_name', ''),
        "foto": getattr(st.experimental_user, 'picture', None),
        "data_cadastro": datetime.now(),
        "ultimo_acesso": datetime.now(),
        "cep": "",             # Campo para armazenar o CEP do usuário
        "telefone": "",        # Campo para armazenar o telefone do usuário
        "instrucoes": "",      # Campo para armazenar informações sobre o usuário
        "data_nascimento": ""  # Campo para armazenar a data de nascimento do usuário
    }

    doc = doc_ref.get()
    if not doc.exists:
        doc_ref.set(dados_usuario)
        # Define um flag para mostrar a mensagem de boas-vindas na próxima página
        st.session_state['show_welcome_message'] = True 
    else:
        doc_ref.update({"ultimo_acesso": datetime.now()})

    if 'login_registrado' not in st.session_state:
        registrar_acao_usuario("Login", "Usuário fez login")
        st.session_state['login_registrado'] = True

def registrar_acao_usuario(acao: str, detalhes: str = ""):
    """
    Registra uma ação do usuário no Firestore.
    
    Args:
        acao: Nome da ação realizada
        detalhes: Detalhes adicionais da ação (opcional)
    """
    if not hasattr(st.experimental_user, 'email'):
        return  # Se não houver email, não registra a ação
        
    db = firestore.client()
    logs_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email).collection("logs")
    
    dados_log = {
        "acao": acao,
        "detalhes": detalhes,
        "data_hora": datetime.now()
    }
    
    logs_ref.add(dados_log)

def obter_idade(data_nascimento):
    """
    Calcula a idade a partir da data de nascimento.
    
    Args:
        data_nascimento: Data de nascimento do usuário
    
    Returns:
        int: Idade do usuário
    """
    if data_nascimento:
        hoje = datetime.now()
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        return idade
    return None

def obter_perfil_usuario():
    """
    Obtém os dados de perfil do usuário atual.
    
    Returns:
        dict: Dicionário com os dados do perfil do usuário
    """
    if not hasattr(st.experimental_user, 'email'):
        return {}  # Retorna um dicionário vazio se não houver email
        
    db = firestore.client()
    doc_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email)
    try:
        doc = doc_ref.get()
        if doc.exists:
            dados = doc.to_dict()
            # Tratar data_nascimento que pode não ser um datetime vindo do Firestore
            dn_firestore = dados.get("data_nascimento")
            idade = None
            if isinstance(dn_firestore, datetime):
                idade = obter_idade(dn_firestore)
            elif isinstance(dn_firestore, str) and dn_firestore:
                try:
                    # Tenta converter string (caso tenha sido salvo assim antes)
                    idade = obter_idade(datetime.fromisoformat(dn_firestore).date())
                except ValueError:
                    pass # Ignora se a string não for formato ISO
                    
            return {
                "nome": dados.get("nome", ""),
                "email": dados.get("email", ""),
                "foto": dados.get("foto", ""),
                "cep": dados.get("cep", ""),
                "telefone": dados.get("telefone", ""),
                "instrucoes": dados.get("instrucoes", ""),
                "idade": idade,  # Adiciona a idade ao perfil
                "data_nascimento": dn_firestore # Retorna o valor original do firestore
            }
    except Exception as e:
        print(f"Erro ao obter perfil para {st.experimental_user.email}: {e}")
        st.warning("Não foi possível carregar os dados do seu perfil.")
        
    return {}

def atualizar_perfil_usuario(dados_perfil):
    """
    Atualiza os dados de perfil do usuário atual.
    
    Args:
        dados_perfil: Dicionário com os dados do perfil a serem atualizados
    
    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário
    """
    if not hasattr(st.experimental_user, 'email'):
        return False  # Retorna False se não houver email
        
    db = firestore.client()
    doc_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email)
    try:
        doc_ref.update(dados_perfil)
        return True
    except Exception as e:
        print(f"Erro ao atualizar perfil para {st.experimental_user.email}: {e}")
        st.error("Ocorreu um erro ao salvar suas informações. Tente novamente.")
        return False

# Funções para gerenciar os chats
def salvar_chat(nome_chat, mensagens):
    """
    Salva um chat no Firestore para o usuário atual.
    
    Args:
        nome_chat: Nome identificador do chat
        mensagens: Lista de mensagens do chat (cada mensagem é um dicionário)
    
    Returns:
        str: ID do chat salvo ou None em caso de erro
    """
    if not hasattr(st.experimental_user, 'email'):
        return None  # Retorna None se não houver email
        
    db = firestore.client()
    chat_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email).collection("chats")
    
    # Se não tiver nome, usa a data/hora como nome
    if not nome_chat:
        nome_chat = f"Chat de {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    try:
        # Verifica se já existe um chat com este nome
        query = chat_ref.where("nome", "==", nome_chat).limit(1).get()
        
        if len(query) > 0:
            # Atualiza o chat existente
            chat_id = query[0].id
            chat_ref.document(chat_id).update({
                "nome": nome_chat,
                "mensagens": mensagens, # Salva mensagens diretamente (sem avatar)
                "ultima_atualizacao": datetime.now()
            })
            return chat_id
        else:
            # Cria um novo chat
            novo_chat = {
                "nome": nome_chat,
                "mensagens": mensagens, # Salva mensagens diretamente (sem avatar)
                "data_criacao": datetime.now(),
                "ultima_atualizacao": datetime.now()
            }
            doc_ref = chat_ref.add(novo_chat)
            return doc_ref[1].id
    except Exception as e:
        print(f"Erro ao salvar chat para {st.experimental_user.email}: {e}")
        st.error("Não foi possível salvar o chat. Verifique sua conexão.")
        return None

def obter_chats():
    """
    Obtém todos os chats do usuário atual.
    
    Returns:
        list: Lista de dicionários, cada um representando um chat
    """
    if not hasattr(st.experimental_user, 'email'):
        return []  # Retorna lista vazia se não houver email
        
    db = firestore.client()
    chats_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email).collection("chats")
    try:
        docs = chats_ref.order_by("ultima_atualizacao", direction=firestore.Query.DESCENDING).stream()
        
        resultado = []
        for chat in docs:
            chat_data = chat.to_dict()
            chat_data["id"] = chat.id
            resultado.append(chat_data)
        return resultado
    except Exception as e:
        print(f"Erro ao obter chats para {st.experimental_user.email}: {e}")
        st.warning("Não foi possível carregar o histórico de chats.")
        return []

def obter_chat(chat_id):
    """
    Obtém um chat específico do usuário atual.
    
    Args:
        chat_id: ID do chat a ser carregado
    
    Returns:
        dict: Dicionário com os dados do chat ou None em caso de erro
    """
    if not hasattr(st.experimental_user, 'email'):
        return None  # Retorna None se não houver email
        
    db = firestore.client()
    chat_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email).collection("chats").document(chat_id)
    try:
        chat = chat_ref.get()
        if chat.exists:
            chat_data = chat.to_dict()
            chat_data["id"] = chat.id
            return chat_data
        else:
            st.warning("Chat não encontrado.")
            return None
    except Exception as e:
        print(f"Erro ao obter chat {chat_id} para {st.experimental_user.email}: {e}")
        st.warning("Não foi possível carregar os dados deste chat.")
        return None

def excluir_chat(chat_id):
    """
    Exclui um chat específico do usuário atual.
    
    Args:
        chat_id: ID do chat a ser excluído
    
    Returns:
        bool: True se a exclusão foi bem-sucedida, False caso contrário
    """
    if not hasattr(st.experimental_user, 'email'):
        return False  # Retorna False se não houver email
        
    db = firestore.client()
    chat_ref = db.collection(COLECAO_USUARIOS).document(st.experimental_user.email).collection("chats").document(chat_id)
    try:
        chat = chat_ref.get()
        if chat.exists:
            chat_ref.delete()
            return True
        else:
            # Não precisa de mensagem, a UI já vai atualizar
            return False
    except Exception as e:
        print(f"Erro ao excluir chat {chat_id} para {st.experimental_user.email}: {e}")
        st.error("Não foi possível excluir o chat.")
        return False










