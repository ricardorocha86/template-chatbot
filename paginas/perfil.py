import streamlit as st
from paginas.funcoes import obter_perfil_usuario, atualizar_perfil_usuario, registrar_acao_usuario
import html
import datetime
import re # Importa regex
from datetime import timedelta
 

def formatar_texto_html(texto):
    """
    Formata o texto para exibição em HTML, preservando quebras de linha e escapando caracteres especiais.
    
    Args:
        texto: Texto a ser formatado
        
    Returns:
        str: Texto formatado para HTML
    """
    if not texto:
        return ""
    
    # Escapar caracteres HTML para evitar injeção de código
    texto_escapado = html.escape(texto)
    
    # Substituir quebras de linha por <br>
    texto_formatado = texto_escapado.replace('\n', '<br>')
    
    return texto_formatado

st.title("Meu Perfil")

# Estilo personalizado
st.markdown("""
<style>
    .perfil-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    .stTextArea > div > div > textarea {
        border-radius: 5px;
    }
    .stButton > button {
        border-radius: 5px;
    }
    .subheader {
        color: #1E3A8A;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .info-label {
        font-weight: bold;
        color: #555;
        margin-bottom: 5px;
    }
    .info-value {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .toggle-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }
    .interesse-item {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Obter dados atuais do perfil
perfil = obter_perfil_usuario()
  

# Inicializar o estado de edição se não existir
if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

# Toggle para editar perfil
col1, col2 = st.columns([3, 1])
with col2:
    # Função para atualizar o modo de edição
    def toggle_modo_edicao():
        st.session_state.modo_edicao = not st.session_state.modo_edicao
        registrar_acao_usuario("Perfil", "Iniciou Edição de Perfil")

    st.toggle("Editar Perfil", 
              value=st.session_state.modo_edicao,
              key="toggle_edicao",
              on_change=toggle_modo_edicao)
  
if st.session_state.modo_edicao:
    # Modo de edição - Formulário para editar informações
    with st.form("formulario_perfil"):
        validacao_ok = True # Flag para controle da validação
        
        st.markdown('<p class="subheader">Informações Cadastrais</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo", value=perfil.get("nome", ""))
        with col2:
            email = st.text_input("Email", value=perfil.get("email", ""), disabled=True)
        
        col1, col2  = st.columns(2)
        with col1:
            cep = st.text_input("CEP", value=perfil.get("cep", ""), 
                               help="Digite apenas os 8 números do CEP.") 
            # Validação do CEP
            if cep and not re.fullmatch(r"\d{8}", cep):
                st.error("Formato de CEP inválido. Digite apenas 8 números.")
                validacao_ok = False
        with col2:
            telefone = st.text_input("Telefone", value=perfil.get("telefone", ""), 
                                    help="Digite DDD + número (10 ou 11 dígitos).")
            # Validação do Telefone
            if telefone and not re.fullmatch(r"\d{10,11}", telefone):
                st.error("Formato de telefone inválido. Digite 10 ou 11 números (DDD + número).")
                validacao_ok = False
        with col1:
            # Deixa o valor padrão como None para o date_input mostrar placeholder
            data_nascimento_atual = perfil.get("data_nascimento")
            if isinstance(data_nascimento_atual, datetime.datetime):
                 data_nascimento_atual = data_nascimento_atual.date()
            else:
                 data_nascimento_atual = None # Garante que é None se não for um datetime
                 
            data_nascimento_input = st.date_input("Data de Nascimento", 
                                            min_value=datetime.date(1930, 1, 1), 
                                            max_value=datetime.date.today() - timedelta(days=365*10), # Ex: Mínimo 10 anos
                                            format="DD/MM/YYYY",
                                            value=data_nascimento_atual # Usa None se não houver data
                                            )
            data_convertida = None
            if data_nascimento_input:
                 data_convertida = datetime.datetime.combine(data_nascimento_input, datetime.datetime.min.time())
      
        st.markdown('<p class="subheader">Instruções Personalizadas do Chatbot</p>', unsafe_allow_html=True)
        instrucoes = st.text_area(
            "Insira suas instruções",
            value=perfil.get("instrucoes", ""),
            height=200,
            placeholder="Insira instruções para personalizar a interação com o chatbot. Exemplos: 'Prefiro respostas diretas e objetivas', 'Explique usando analogias do dia a dia', 'Me ajude focando em exercícios práticos'. Estas instruções serão aplicadas em todas as interações. Funcionalidade em desenvolvimento...🚧"
        )
        st.divider()
        dados_atualizados = {
                "nome": nome,
                "cep": cep, 
                "telefone": telefone, 
                "instrucoes": instrucoes,
                "data_nascimento": data_convertida
            }  
        
        submitted = st.form_submit_button(
            "Salvar Alterações",
            type="primary",
            use_container_width=True, 
        )

        if submitted and validacao_ok: # Só atualiza se a validação passou
            atualizar_perfil_usuario(dados_atualizados)
            registrar_acao_usuario("Perfil", "Perfil Atualizado com Sucesso")
            st.toast("✅ Perfil Atualizado!") 
            st.session_state.modo_edicao = False 
            st.rerun()
        elif submitted and not validacao_ok:
            st.warning("Existem erros no formulário. Por favor, corrija antes de salvar.")


else:
    # Modo de visualização - Exibir informações do perfil
    st.container()
    with st.container():
        # Adicionar foto de perfil
        foto_url = perfil.get("foto", "")
        col_foto, col_info = st.columns([1, 7])
        
        with col_foto:
            if foto_url:
                st.image(foto_url,  use_container_width=False)
                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
            else:
                # Exibir avatar padrão se não houver foto
                st.markdown("""
                <div style="width: 80px; height: 80px; border-radius: 50%; background-color: #e0e0e0; 
                display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 30px; color: #757575;">👤</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_info:
            st.markdown('<p style="font-size: 16px; margin-bottom: -20px;">Nome Completo</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-label" style="font-size: 30px; font-weight: bold; color: rgba(0, 0, 0, 0.8);">{perfil.get("nome", "Não informado")}</p>', unsafe_allow_html=True)

    st.divider()
    
    # Informações principais em duas colunas
    st.markdown('<p class="subheader">Informações Cadastrais</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('<p class="info-label">Idade</p>', unsafe_allow_html=True)
        idade_valor = perfil.get("idade") # Obtém o valor da idade (pode ser None)
        idade_texto = f"{idade_valor} anos" if idade_valor is not None else "Não informado"
        st.markdown(f'<p class="info-value">{idade_texto}</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="info-label">Email</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-value">{perfil.get("email", "Não informado")}</p>', unsafe_allow_html=True)
    
    col1, col2  = st.columns(2)
 
    with col1:
        st.markdown('<p class="info-label">CEP</p>', unsafe_allow_html=True)
        cep_valor = perfil.get("cep", "")
        if cep_valor and len(cep_valor) == 8:
            cep_formatado = f"{cep_valor[:5]}-{cep_valor[5:]}"
            st.markdown(f'<p class="info-value">{cep_formatado}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="info-value">{cep_valor or "Não informado"}</p>', unsafe_allow_html=True)
 
    with col2:
        st.markdown('<p class="info-label">Telefone</p>', unsafe_allow_html=True)
        telefone_valor = perfil.get("telefone", "")
        if telefone_valor:
            if len(telefone_valor) == 11:  # Celular com DDD
                telefone_formatado = f"({telefone_valor[:2]}) {telefone_valor[2:7]}-{telefone_valor[7:]}"
            elif len(telefone_valor) == 10:  # Fixo com DDD
                telefone_formatado = f"({telefone_valor[:2]}) {telefone_valor[2:6]}-{telefone_valor[6:]}"
            else:
                telefone_formatado = telefone_valor
            st.markdown(f'<p class="info-value">{telefone_formatado}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="info-value">Não informado</p>', unsafe_allow_html=True)
     
  
    # Seção Instruções Personalizadas   
    with st.container():
        st.markdown('<p class="subheader">Instruções Personalizadas do Chatbot</p>', unsafe_allow_html=True)
        instrucoes = perfil.get("instrucoes", "")
        if instrucoes:
            # Usar a função de formatação para preservar quebras de linha
            instrucoes_formatado = formatar_texto_html(instrucoes)
            st.markdown(f'<div class="info-value">{instrucoes_formatado}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="info-value">Nenhuma informação disponível</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.page_link("paginas/chatbot.py", label=" Voltar para as conversas", icon="🏃", )




