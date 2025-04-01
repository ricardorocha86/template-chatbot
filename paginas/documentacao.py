import streamlit as st
import os

st.title("Documentação do Template")

# Caminho do arquivo README.md
readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')

# Ler o conteúdo do README.md
with open(readme_path, 'r', encoding='utf-8') as file:
    readme_content = file.read()

# Exibir o conteúdo do README
st.markdown(readme_content)

st.divider()
# Botão para voltar para o chatbot
st.page_link("paginas/chatbot.py", label=" Voltar para as conversas", icon="🏃") 