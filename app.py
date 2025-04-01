import streamlit as st 
from paginas.funcoes import inicializar_firebase 
import os # Importar os

# Inicializa o Firebase
inicializar_firebase() 

st.set_page_config(
    page_title="Chatbot Template",  # Título genérico
    page_icon="arquivos/avatar2.png",                          # Ícone genérico (sugerir troca no README)
    layout='wide',                       # Melhor aproveitamento do espaço
    initial_sidebar_state="expanded"
)
 
# Estilo CSS personalizado
st.markdown("""
<style>
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        max-width: 500px;
        margin: auto;
    }
    .welcome-text {
        color: #1f1f1f;
        text-align: center;
    }
    .subtitle-text {
        color: #666;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    .terms-text {
        font-size: 0.75em;
        color: #888;
        margin-top: 15px;
        text-align: center;
        line-height: 1.4;
    }
    .terms-link {
        color: #3399FF; /* Cor azul para o link */
        text-decoration: none;
        cursor: pointer;
    }
    .terms-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)


# Verificação de login
if not hasattr(st.experimental_user, 'is_logged_in') or not st.experimental_user.is_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo centralizada
        st.image('arquivos/capa.png', width=200, use_container_width=True)
        st.markdown('<h1 class="welcome-text">ChatBot Template</h1>', unsafe_allow_html=True) # Texto genérico
        st.markdown('<p class="subtitle-text" style="text-align: center;">Faça login para iniciar o chat.</p>', unsafe_allow_html=True) # Texto genérico
        # Botão de login
        if st.button("Login com Google", type="primary", use_container_width=True, icon=':material/login:'):
            st.login()
        
        # Carrega conteúdo dos Termos para o Popover
        termos_content = "Não foi possível carregar os Termos de Uso e Política de Privacidade."
        try:
            termos_path = os.path.join(os.path.dirname(__file__), 'termos_e_privacidade.md')
            with open(termos_path, 'r', encoding='utf-8') as file:
                termos_content = file.read()
        except Exception as e:
            print(f"Erro ao carregar termos em app.py: {e}") # Log do erro
            # Mantém a mensagem padrão de erro
            
        # Popover com os termos carregados
        with st.popover("Ao fazer login, você concorda com nossos Termos de Uso e Política de Privacidade", use_container_width=True):
            st.markdown(termos_content, unsafe_allow_html=True)
            
 
else:
    # Logo
    st.logo('arquivos/logo.png')


    # Configuração das páginas após login
    paginas = {
        "Páginas": [ 
            st.Page("paginas/perfil.py", title="Meu Perfil", icon='👤'),
            st.Page("paginas/termos.py", title="Termos e Privacidade", icon=':material/privacy_tip:'), # Adiciona página de Termos
            st.Page("paginas/documentacao.py", title="Documentação", icon='📄')
        ],
        "Aplicativos": [
            st.Page("paginas/chatbot.py", title="Chatbot", default=True, icon='🤖'), # Título genérico
        ],
        "Admin": [
            st.Page("paginas/admin.py", title="Banco de Dados do App", icon='📊'),
        ],
    }
    
  
    # Navegação
    pg = st.navigation(paginas, position="hidden")
    pg.run()
 