import streamlit as st 

from datetime import datetime, timedelta, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from firebase_admin import firestore
from paginas.funcoes import registrar_acao_usuario, COLECAO_USUARIOS

st.title("🔐 Painel Administrativo")

st.write("Aplicativo desenvolvido por [@ricardorocha86](https://www.linkedin.com/in/ricardorocha86/)")
st.write('Versão 0.0.2')

senha = st.text_input('Senha de administrador:', type='password')
if senha == 'admim':    #SENHA PARA ACESSAR O BANCO DE DADOS - RECURSO PROVISORIO PARA PROTOTIPAGEM, REQUER MAIS SEGURANÇA NISSO
    # Inicializar o cliente Firestore
    db = firestore.client()
    
    # Criar guias para organizar o dashboard
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "👥 Usuários", "🔍 Dados Detalhados"])
    
    with tab1:
        st.header("Visão Geral do Sistema")
        
        # Obter dados gerais para o dashboard
        usuarios = db.collection(COLECAO_USUARIOS).get()
        dados_usuarios = []
        total_acoes = 0
        usuarios_ativos_7dias = 0
        hoje = datetime.now(timezone.utc)
        data_7dias_atras = hoje - timedelta(days=7)
        
        # Dados para gráficos
        acoes_por_dia = {}
        acoes_por_tipo = {}
        
        for usuario in usuarios:
            dados = usuario.to_dict()
            email = dados.get("email", "")
            ultimo_acesso = dados.get("ultimo_acesso", None)
            
            # Contar usuários ativos nos últimos 7 dias
            if ultimo_acesso and ultimo_acesso > data_7dias_atras:
                usuarios_ativos_7dias += 1
            
            # Obter logs do usuário
            logs = db.collection(COLECAO_USUARIOS).document(email).collection("logs").get()
            acoes_usuario = len(logs)
            total_acoes += acoes_usuario
            
            # Processar logs para estatísticas
            for log in logs:
                log_data = log.to_dict()
                data_hora = log_data.get('data_hora', None)
                tipo_acao = log_data.get('acao', 'Desconhecida')
                
                if data_hora:
                    data_str = data_hora.strftime('%d/%m/%Y')
                    acoes_por_dia[data_str] = acoes_por_dia.get(data_str, 0) + 1
                
                acoes_por_tipo[tipo_acao] = acoes_por_tipo.get(tipo_acao, 0) + 1
            
            # Adicionar usuário à lista
            dados_usuarios.append({
                "Nome": dados.get("nome", ""),
                "Email": email,
                "Primeiro Nome": dados.get("primeiro_nome", ""),
                "Data Cadastro": dados.get("data_cadastro", "").strftime("%d/%m/%Y %H:%M:%S") if dados.get("data_cadastro") else "",
                "Último Acesso": dados.get("ultimo_acesso", "").strftime("%d/%m/%Y %H:%M:%S") if dados.get("ultimo_acesso") else "",
                "Ações Totais": acoes_usuario,
            })
        
        # Métricas principais
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Usuários", len(dados_usuarios))
        with col2:
            st.metric("Usuários Ativos (7 dias)", usuarios_ativos_7dias)
        with col3:
            st.metric("Total de Ações Registradas", total_acoes)
        
        # Gráficos para a visão geral
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Atividade por Dia")
            if acoes_por_dia:
                df_dias = pd.DataFrame({
                    'Data': list(acoes_por_dia.keys()),
                    'Ações': list(acoes_por_dia.values())
                })
                df_dias = df_dias.sort_values('Data')
                fig = px.bar(df_dias, x='Data', y='Ações', title='Ações por Dia')
                fig.update_layout(xaxis_title='Data', yaxis_title='Número de Ações')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há dados suficientes para gerar o gráfico de atividade diária.")
        
        with col2:
            st.subheader("Tipos de Ação")
            if acoes_por_tipo:
                df_tipos = pd.DataFrame({
                    'Tipo': list(acoes_por_tipo.keys()),
                    'Contagem': list(acoes_por_tipo.values())
                })
                df_tipos = df_tipos.sort_values('Contagem', ascending=False)
                fig = px.pie(df_tipos, values='Contagem', names='Tipo', title='Distribuição de Tipos de Ação')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há dados suficientes para gerar o gráfico de tipos de ação.")
    
    with tab2:
        st.header("Gerenciamento de Usuários")
        
        # Criar DataFrame com dados de usuários
        df_usuarios = pd.DataFrame(dados_usuarios)
        
        # Filtros para usuários
        col1, col2 = st.columns(2)
        with col1:
            filtro_nome = st.text_input("Filtrar por Nome:")
        with col2:
            filtro_email = st.text_input("Filtrar por Email:")
        
        # Aplicar filtros
        df_filtrado = df_usuarios.copy()
        if filtro_nome:
            df_filtrado = df_filtrado[df_filtrado['Nome'].str.contains(filtro_nome, case=False)]
        if filtro_email:
            df_filtrado = df_filtrado[df_filtrado['Email'].str.contains(filtro_email, case=False)]
        
        # Exibir tabela de usuários com ordem personalizada
        st.dataframe(
            df_filtrado.sort_values(by="Último Acesso", ascending=False), 
            hide_index=True, 
            use_container_width=True
        )
        
        # Detalhes do usuário
        st.write("### Detalhes do Usuário")
        usuarios_emails = df_usuarios['Email'].tolist()
        usuario_selecionado = st.selectbox("Selecione um usuário para ver detalhes:", usuarios_emails)
        
        if usuario_selecionado:
            # Buscar logs do usuário
            logs = db.collection(COLECAO_USUARIOS).document(usuario_selecionado).collection("logs").get()
            
            # Buscar chats do usuário
            chats = db.collection(COLECAO_USUARIOS).document(usuario_selecionado).collection("chats").get()
            total_chats = len(chats)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Ações", len(logs))
            with col2:
                st.metric("Total de Chats", total_chats)
            
            # Exibir tabs para ações e chats
            tab_acoes, tab_chats = st.tabs(["Ações do Usuário", "Chats do Usuário"])
            
            with tab_acoes:
                dados_acoes = []
                for log in logs:
                    log_data = log.to_dict()
                    data_hora = log_data.get('data_hora', '')
                    dados_acoes.append({
                        "Ação": log_data.get('acao', ''),
                        "Data/Hora": data_hora,  # Mantém o objeto datetime original
                        "Data/Hora Formatada": data_hora.strftime('%d/%m/%Y %H:%M:%S') if data_hora else '',
                        "Observações": str(log_data.get('detalhes', ''))
                    })
                
                if dados_acoes:
                    df_acoes = pd.DataFrame(dados_acoes)
                    # Ordena pelo campo datetime original
                    df_acoes = df_acoes.sort_values(by="Data/Hora", ascending=False)
                    # Exclui a coluna de datetime original e exibe
                    df_acoes_display = df_acoes.drop(columns=["Data/Hora"])
                    st.dataframe(df_acoes_display, hide_index=True, use_container_width=True)
                    
                    # Gráfico de atividade do usuário
                    st.subheader(f"Atividade de {usuario_selecionado}")
                    
                    # Agrupar ações por dia
                    df_acoes['Data'] = df_acoes['Data/Hora'].apply(lambda x: x.strftime('%d/%m/%Y') if x else '')
                    acoes_por_dia = df_acoes['Data'].value_counts().reset_index()
                    acoes_por_dia.columns = ['Data', 'Contagem']
                    acoes_por_dia = acoes_por_dia.sort_values('Data')
                    
                    fig = px.line(acoes_por_dia, x='Data', y='Contagem', markers=True,
                                title=f'Atividade Diária de {usuario_selecionado}')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.text("Nenhuma ação registrada para este usuário")
            
            with tab_chats:
                dados_chats = []
                for chat in chats:
                    chat_data = chat.to_dict()
                    
                    # Contar mensagens
                    mensagens = chat_data.get('mensagens', [])
                    num_mensagens = len(mensagens)
                    
                    # Pegar data de criação e última atualização
                    data_criacao = chat_data.get('data_criacao', '')
                    ultima_atualizacao = chat_data.get('ultima_atualizacao', '')
                    
                    dados_chats.append({
                        "Nome": chat_data.get('nome', 'Chat sem nome'),
                        "Mensagens": num_mensagens,
                        "Data Criação": data_criacao.strftime('%d/%m/%Y %H:%M:%S') if data_criacao else '',
                        "Última Atualização": ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S') if ultima_atualizacao else '',
                        "ID": chat.id
                    })
                
                if dados_chats:
                    df_chats = pd.DataFrame(dados_chats)
                    st.dataframe(df_chats.sort_values(by="Última Atualização", ascending=False), 
                                hide_index=True, use_container_width=True)
                    
                    # Permitir visualização do conteúdo de um chat
                    chat_ids = df_chats['ID'].tolist()
                    if chat_ids:
                        chat_selecionado = st.selectbox("Selecione um chat para ver as mensagens:", chat_ids)
                        if chat_selecionado:
                            chat_doc = db.collection(COLECAO_USUARIOS).document(usuario_selecionado).collection("chats").document(chat_selecionado).get()
                            if chat_doc.exists:
                                chat_data = chat_doc.to_dict()
                                mensagens = chat_data.get('mensagens', [])
                                
                                st.subheader(f"Mensagens do chat: {chat_data.get('nome', 'Chat sem nome')}")
                                
                                for i, msg in enumerate(mensagens):
                                    role = msg.get('role', '')
                                    content = msg.get('content', '')
                                    
                                    if role == "user":
                                        st.markdown(f"**Usuário**: {content}")
                                    elif role == "assistant":
                                        st.markdown(f"**Assistente**: {content}")
                                    
                                    if i < len(mensagens) - 1:
                                        st.divider()
                else:
                    st.text("Nenhum chat encontrado para este usuário")
    
    with tab3:
        st.header("Dados Detalhados")
        
        # Opções para visualização
        visualizacao = st.selectbox("O que deseja visualizar?", 
                                   ["Todos os Logs", "Usuários por Período", "Exportar Dados"])
        
        if visualizacao == "Todos os Logs":
            # Período para análise
            periodo = st.selectbox("Período de análise:", 
                                 ["Últimos 7 dias", "Últimos 30 dias", "Todo o período"])
            
            # Definir data de corte com base no período selecionado, usando UTC
            data_corte = hoje
            if periodo == "Últimos 7 dias":
                data_corte = hoje - timedelta(days=7)
            elif periodo == "Últimos 30 dias":
                data_corte = hoje - timedelta(days=30)
            
            # Coletar todos os logs no período selecionado
            todos_logs = []
            for usuario in dados_usuarios:
                email = usuario["Email"]
                logs = db.collection(COLECAO_USUARIOS).document(email).collection("logs").get()
                
                for log in logs:
                    log_data = log.to_dict()
                    data_hora = log_data.get('data_hora', None)
                    
                    if data_hora and (periodo == "Todo o período" or data_hora >= data_corte):
                        todos_logs.append({
                            "Usuario": email,
                            "Acao": log_data.get('acao', 'Desconhecida'),
                            "Data_Hora": data_hora,  # Objeto datetime completo para ordenação
                            "Data": data_hora.strftime('%d/%m/%Y'),
                            "Hora": data_hora.strftime('%H:00'),
                            "Detalhes": str(log_data.get('detalhes', ''))
                        })
            
            # Criar DataFrame com todos os logs
            df_todos_logs = pd.DataFrame(todos_logs)
            
            if not df_todos_logs.empty:
                # Ordenar o DataFrame principal por Data_Hora para uso consistente
                df_todos_logs = df_todos_logs.sort_values(by="Data_Hora", ascending=False)
                
                # Exibir tabela com logs filtrados
                st.subheader("Logs Detalhados")
                df_logs_display = df_todos_logs[['Usuario', 'Acao', 'Data', 'Hora', 'Detalhes']]
                st.dataframe(df_logs_display, hide_index=True, use_container_width=True)
                
                # Busca por palavra-chave
                st.subheader("Busca por Palavra-chave nos Logs")
                palavra_chave = st.text_input("Digite a palavra-chave para buscar:")
                if palavra_chave:
                    filtro_palavra = df_logs_display[
                        df_logs_display['Acao'].str.contains(palavra_chave, case=False) | 
                        df_logs_display['Detalhes'].str.contains(palavra_chave, case=False)
                    ]
                    
                    if not filtro_palavra.empty:
                        st.write(f"Foram encontrados {len(filtro_palavra)} resultados para '{palavra_chave}':")
                        st.dataframe(filtro_palavra, hide_index=True, use_container_width=True)
                    else:
                        st.info(f"Nenhum resultado encontrado para '{palavra_chave}'.")
            else:
                st.info(f"Não há dados de logs para o período selecionado ({periodo}).")
                
        elif visualizacao == "Usuários por Período":
            # Agrupar usuários por data de cadastro
            df_usuarios['Data Cadastro Curta'] = df_usuarios['Data Cadastro'].str.split(' ').str[0]
            usuarios_por_dia = df_usuarios['Data Cadastro Curta'].value_counts().reset_index()
            usuarios_por_dia.columns = ['Data', 'Novos Usuários']
            usuarios_por_dia = usuarios_por_dia.sort_values('Data')
            
            fig = px.bar(usuarios_por_dia, x='Data', y='Novos Usuários',
                       title='Novos Usuários por Dia')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela completa
            st.subheader("Detalhamento de Usuários por Data de Cadastro")
            st.dataframe(
                df_usuarios[['Nome', 'Email', 'Data Cadastro', 'Último Acesso']],
                hide_index=True,
                use_container_width=True
            )
            
        elif visualizacao == "Exportar Dados":
            # Opção para exportar dados
            st.subheader("Exportar Dados")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Exportar Lista de Usuários (CSV)", use_container_width=True):
                    csv = df_usuarios.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{COLECAO_USUARIOS}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
            with col2:
                if st.button("Exportar Todos os Logs (CSV)", use_container_width=True):
                    # Criar DataFrame com todos os logs para exportação
                    todos_logs_export = []
                    for usuario in dados_usuarios:
                        email = usuario["Email"]
                        logs = db.collection(COLECAO_USUARIOS).document(email).collection("logs").get()
                        
                        for log in logs:
                            log_data = log.to_dict()
                            data_hora = log_data.get('data_hora', '')
                            todos_logs_export.append({
                                "Usuario": email,
                                "Acao": log_data.get('acao', ''),
                                "Data_Hora": data_hora.strftime('%d/%m/%Y %H:%M:%S') if data_hora else '',
                                "Detalhes": str(log_data.get('detalhes', ''))
                            })
                    
                    df_logs_export = pd.DataFrame(todos_logs_export)
                    csv = df_logs_export.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"logs_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )

else:
    st.warning("Por favor, digite a senha correta para acessar o painel administrativo.")

st.divider()
st.page_link("paginas/chatbot.py", label=" Voltar para as conversas", icon="🏃", )
