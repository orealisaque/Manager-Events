import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os

# Função para criar card do evento
def criar_card_evento(evento, tempo_str, borda_cor):
    return f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h2 style="margin: 0; color: #ffffff; font-size: 1.8em;">{evento['Nome do Evento']}</h2>
            <span class="status-tag">{evento['Andamento']}</span>
        </div>
        <div class="info-container">
            <p style="margin: 10px 0; color: #ff3333; font-size: 1.2em;">{tempo_str}</p>
            <p style="margin: 10px 0; color: #888888; font-size: 1.1em;">{evento['Período']}</p>
            <div style="display: flex; align-items: center; margin: 15px 0;">
                <span style="font-size: 1.3em;" class="temp-{temperatura_to_emoji(evento['Temperatura']).split()[1].lower()}">
                    {temperatura_to_emoji(evento['Temperatura'])}
                </span>
            </div>
        </div>
        <div style="display: flex; gap: 15px; margin-top: 20px;">
            {f'<a href="{evento["Link Evento"]}" target="_blank" class="link-button">🔗 Link do Evento</a>' if pd.notna(evento["Link Evento"]) else ''}
            {f'<a href="{evento["Link do Grupo"]}" target="_blank" class="link-button">👥 Link do Grupo</a>' if pd.notna(evento["Link do Grupo"]) else ''}
        </div>
    </div>
    """

# Configuração da página
st.set_page_config(
    page_title="Controle de Lançamentos",
    page_icon="📅",
    initial_sidebar_state="expanded"
)

# Configuração do tema escuro
st.markdown("""
    <style>
    /* Tema Geral */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Inputs e Selects */
    .stSelectbox, .stMultiSelect, .stDateInput, .stTextInput {
        background-color: #111111;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 8px;
    }
    
    .stTextInput > div > div > input {
        color: #ffffff !important;
        background-color: #111111 !important;
    }
    
    /* Links */
    div[data-testid="stMarkdownContainer"] a {
        color: #ff3333;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMarkdownContainer"] a:hover {
        background-color: rgba(255, 51, 51, 0.1);
    }
    
    /* Botões */
    .stButton > button {
        background-color: #ff3333;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #cc0000;
        transform: translateY(-2px);
    }
    
    /* Cards e Containers */
    .card {
        background-color: #111111;
        padding: 25px;
        border-radius: 8px;
        margin: 20px 0;
        border: 1px solid #ff3333;
        position: relative;
        overflow: hidden;
        animation: borderGlow 2s infinite;
    }
    
    @keyframes borderGlow {
        0% { box-shadow: 0 0 5px #ff3333; }
        50% { box-shadow: 0 0 20px #ff3333; }
        100% { box-shadow: 0 0 5px #ff3333; }
    }
    
    /* Títulos */
    .big-title {
        font-size: 3.5em;
        font-weight: 800;
        text-align: center;
        margin: 40px 0;
        padding: 30px;
        background-color: #111111;
        border-radius: 8px;
        position: relative;
        overflow: hidden;
        animation: titleBorder 4s infinite;
    }
    
    @keyframes titleBorder {
        0% { box-shadow: 0 0 0 2px #ff3333; }
        50% { box-shadow: 0 0 0 4px #cc0000; }
        100% { box-shadow: 0 0 0 2px #ff3333; }
    }
    
    .section-title {
        color: #ff3333;
        font-size: 2.5em;
        font-weight: 600;
        margin: 30px 0;
        padding: 20px 0;
        border-bottom: 2px solid #ff3333;
        animation: borderPulse 2s infinite;
    }
    
    @keyframes borderPulse {
        0% { border-bottom-color: #ff3333; }
        50% { border-bottom-color: #cc0000; }
        100% { border-bottom-color: #ff3333; }
    }
    
    /* Status Tags */
    .status-tag {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 1em;
        margin: 8px;
        font-weight: 500;
        border: 1px solid #ff3333;
        background-color: rgba(255, 51, 51, 0.1);
    }
    
    /* Temperatura Tags */
    .temp-frio { color: #00ffff; }
    .temp-morno { color: #ffff00; }
    .temp-quente { color: #ff3333; }
    
    /* Forms */
    .stForm {
        background-color: #111111;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #333333;
        margin: 20px 0;
    }
    
    /* Tabelas */
    .dataframe {
        background-color: #111111 !important;
        border: 1px solid #333333;
        border-radius: 8px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .dataframe th {
        background-color: #1a1a1a !important;
        color: #ff3333 !important;
        padding: 12px !important;
    }
    
    .dataframe td {
        background-color: #111111 !important;
        color: white !important;
        padding: 12px !important;
    }
    
    /* Divisores de Seção */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #ff3333, transparent);
        margin: 40px 0;
        animation: dividerGlow 2s infinite;
    }
    
    @keyframes dividerGlow {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    /* Container de Informações */
    .info-container {
        background-color: #111111;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #333333;
    }
    
    /* Espaçamento de Elementos */
    .stMarkdown {
        margin: 20px 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #111111;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #ff3333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #cc0000;
    }
    </style>
""", unsafe_allow_html=True)

# Função para carregar as credenciais do Google Calendar
def load_google_credentials():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return credentials
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {str(e)}")
        return None

# Função para adicionar evento ao Google Calendar
def add_to_calendar(event_name, event_date, event_link):
    credentials = load_google_credentials()
    if credentials:
        try:
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': event_name,
                'description': f"Link do evento: {event_link}",
                'start': {
                    'dateTime': event_date.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': event_date.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar evento: {str(e)}")
            return False

# Função para converter temperatura em emoji
def temperatura_to_emoji(temp):
    if temp <= 3:
        return "❄️ FRIO"
    elif temp <= 7:
        return "🙃 MORNO"
    else:
        return "🔥 QUENTE"

# Função para converter emoji em valor numérico
def emoji_to_temperatura(emoji):
    if emoji == "❄️ FRIO":
        return 1
    elif emoji == "🙃 MORNO":
        return 5
    else:  # "🔥 QUENTE"
        return 10

# Função para salvar dados no CSV
def save_data_to_csv():
    st.session_state.data.to_csv('dados_iniciais.csv', index=False)

# Inicialização do estado da sessão
if 'data' not in st.session_state:
    # Tenta carregar dados do CSV se existir
    if os.path.exists('dados_iniciais.csv'):
        df = pd.read_csv('dados_iniciais.csv')
        # Converter colunas de data
        df['Data do Evento'] = pd.to_datetime(df['Data do Evento'])
        df['Data de Fim'] = pd.to_datetime(df['Data de Fim'])
        st.session_state.data = df
    else:
        st.session_state.data = pd.DataFrame({
            'Nome do Evento': [],
            'Data do Evento': [],
            'Data de Fim': [],
            'Link Evento': [],
            'Andamento': [],
            'Temperatura': [],
            'Link do Grupo': [],
            'Período': []
        })

# Inicialização do estado de edição
if 'editing' not in st.session_state:
    st.session_state.editing = False
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Menu lateral
with st.sidebar:
    selected = option_menu(
        "Menu Principal",
        ["Dashboard", "Adicionar Lançamento", "Visualizar Lançamentos", "Tabela"],
        icons=['graph-up', 'plus-circle', 'table', 'list-task'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#2b2b2b"},
            "icon": {"color": "#ffffff", "font-size": "25px"}, 
            "nav-link": {"color": "#ffffff", "font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#4b4b4b"},
            "nav-link-selected": {"background-color": "#4b4b4b"},
        }
    )

# Página Dashboard
if selected == "Dashboard":
    st.markdown('<h1 class="big-title">📊 Dashboard de Lançamentos</h1>', unsafe_allow_html=True)
    
    if not st.session_state.data.empty:
        # Próximos eventos primeiro
        st.markdown('<h2 style="color: #4CAF50; margin-bottom: 20px;">📅 Próximos Eventos</h2>', unsafe_allow_html=True)
        
        # Filtrar apenas eventos que não começaram
        data_atual = pd.Timestamp.now()
        eventos_disponiveis = st.session_state.data[
            (st.session_state.data['Data do Evento'] >= data_atual) &
            (st.session_state.data['Andamento'] == 'Não começou')
        ].sort_values('Data do Evento')
        
        if not eventos_disponiveis.empty:
            # Criar colunas para os filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_dias = st.number_input(
                    "Mostrar eventos dos próximos X dias",
                    min_value=1,
                    max_value=365,
                    value=30
                )
            
            with col2:
                filtro_status = ["Não começou"]  # Removido o multiselect, agora é fixo
            
            with col3:
                filtro_temp = st.multiselect(
                    "Temperatura",
                    options=["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"]
                )
            
            # Aplicar filtros
            data_limite = data_atual + pd.Timedelta(days=filtro_dias)
            eventos_filtrados = eventos_disponiveis[
                (eventos_disponiveis['Data do Evento'] <= data_limite) &
                (eventos_disponiveis['Andamento'].isin(filtro_status))
            ]
            
            if filtro_temp:
                eventos_filtrados['Temperatura_Label'] = eventos_filtrados['Temperatura'].apply(temperatura_to_emoji)
                eventos_filtrados = eventos_filtrados[eventos_filtrados['Temperatura_Label'].isin(filtro_temp)]
            
            # Criar lista de seleção de eventos
            opcoes_eventos = []
            for _, evento in eventos_filtrados.iterrows():
                dias_ate = (evento['Data do Evento'] - data_atual).days
                opcao = f"{evento['Nome do Evento']} - Em {dias_ate} dias - {temperatura_to_emoji(evento['Temperatura'])}"
                opcoes_eventos.append(opcao)
            
            eventos_selecionados = st.multiselect(
                "Selecione os eventos que deseja acompanhar:",
                options=opcoes_eventos,
                default=opcoes_eventos[:3] if len(opcoes_eventos) > 0 else []
            )
            
            # Mostrar cards dos eventos selecionados
            if eventos_selecionados:
                st.markdown("### 📌 Seus Eventos Selecionados")
                
                for evento_str in eventos_selecionados:
                    nome_evento = evento_str.split(" - ")[0]
                    evento = eventos_filtrados[eventos_filtrados['Nome do Evento'] == nome_evento].iloc[0]
                    
                    dias_ate_evento = (evento['Data do Evento'] - data_atual).days
                    horas_ate_evento = ((evento['Data do Evento'] - data_atual).seconds // 3600)
                    
                    # Criar string de tempo até o evento
                    if dias_ate_evento > 0:
                        tempo_str = f"🕒 Em {dias_ate_evento} dias"
                    elif horas_ate_evento > 0:
                        tempo_str = f"🕒 Em {horas_ate_evento} horas"
                    else:
                        minutos = ((evento['Data do Evento'] - data_atual).seconds // 60) % 60
                        tempo_str = f"🕒 Em {minutos} minutos"
                    
                    # Definir cor da borda baseada no status
                    borda_cor = "#4CAF50" if evento['Andamento'] == "Não começou" else "#FFA500"
                    
                    # Criar card do evento
                    st.markdown(criar_card_evento(evento, tempo_str, borda_cor), unsafe_allow_html=True)
            else:
                st.info("Selecione os eventos que deseja acompanhar acima.")
        else:
            st.info("Não há eventos próximos agendados.")
        
        # Gráficos abaixo dos próximos eventos
        st.markdown('<h2 style="color: #4CAF50; margin: 30px 0 20px 0;">📈 Estatísticas</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de status com cores personalizadas
            status_count = st.session_state.data['Andamento'].value_counts()
            cores_status = {
                'Não começou': '#4CAF50',
                'Em andamento': '#FFA500',
                'Finalizado': '#2196F3'
            }
            cores_status_lista = [cores_status[status] for status in status_count.index]
            
            fig_status = px.pie(
                values=status_count.values,
                names=status_count.index,
                title='Distribuição por Status',
                color_discrete_sequence=cores_status_lista
            )
            fig_status.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font_size=20,
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Gráfico de temperatura com cores personalizadas
            st.session_state.data['Temperatura_Label'] = st.session_state.data['Temperatura'].apply(temperatura_to_emoji)
            temp_count = st.session_state.data['Temperatura_Label'].value_counts()
            
            cores_temp = {
                '❄️ FRIO': '#00BCD4',
                '🙃 MORNO': '#FFA500',
                '🔥 QUENTE': '#F44336'
            }
            cores_temp_lista = [cores_temp[temp] for temp in temp_count.index]
            
            fig_temp = px.bar(
                x=temp_count.index,
                y=temp_count.values,
                title='Distribuição por Temperatura',
                color=temp_count.index,
                color_discrete_map=cores_temp
            )
            fig_temp.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font_size=20,
                showlegend=False,
                xaxis=dict(title='', gridcolor='rgba(128,128,128,0.2)'),
                yaxis=dict(title='Quantidade', gridcolor='rgba(128,128,128,0.2)')
            )
            st.plotly_chart(fig_temp, use_container_width=True)

# Página Adicionar Lançamento
elif selected == "Adicionar Lançamento":
    st.markdown('<h1 class="big-title">➕ Adicionar Novo Lançamento</h1>', unsafe_allow_html=True)
    
    with st.form("novo_lancamento"):
        nome = st.text_input("Nome do Evento")
        
        # Datas de início e fim
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Data de Início")
            data_inicio = st.date_input("Data", key="data_inicio")
            hora_inicio = st.time_input("Hora", key="hora_inicio")
        
        with col2:
            st.markdown("### Data de Fim")
            data_fim = st.date_input("Data", key="data_fim", value=data_inicio)
            hora_fim = st.time_input("Hora", key="hora_fim", value=hora_inicio)
        
        # Validação das datas
        datetime_inicio = datetime.combine(data_inicio, hora_inicio)
        datetime_fim = datetime.combine(data_fim, hora_fim)
        
        if datetime_fim < datetime_inicio:
            st.error("A data de fim não pode ser anterior à data de início!")
        
        # Formatação do período para exibição (mais simples, apenas com hora)
        periodo = f"{data_inicio.strftime('%d/%m/%Y')} {hora_inicio.strftime('%H')}h - {data_fim.strftime('%d/%m/%Y')} {hora_fim.strftime('%H')}h"
        st.markdown(f"""
        <div style="
            background-color: #2b2b2b;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 3px solid #4CAF50;
        ">
            <p style="margin: 0;"><strong>Período:</strong> {periodo}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Outros campos
        link_evento = st.text_input("Link do Evento")
        andamento = st.selectbox("Andamento", ["Não começou", "Em andamento", "Finalizado"])
        temperatura = emoji_to_temperatura(
            st.selectbox("Temperatura", 
                        ["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"],
                        format_func=lambda x: x)
        )
        link_grupo = st.text_input("Link do Grupo")
        
        # Botão de submit
        submitted = st.form_submit_button("Adicionar")
        
        if submitted and nome:
            if datetime_fim >= datetime_inicio:
                # Verificar se já existe evento com o mesmo nome
                evento_existente = st.session_state.data[
                    st.session_state.data['Nome do Evento'].str.lower() == nome.lower()
                ]
                
                # Verificar se já existe evento no mesmo período
                eventos_periodo = st.session_state.data[
                    (st.session_state.data['Data do Evento'] <= datetime_fim) &
                    (st.session_state.data['Data de Fim'] >= datetime_inicio)
                ]
                
                if not evento_existente.empty:
                    st.error("Já existe um evento com este nome!")
                elif not eventos_periodo.empty:
                    eventos_conflito = ", ".join(eventos_periodo['Nome do Evento'].tolist())
                    st.error(f"Existe(m) evento(s) conflitante(s) no mesmo período: {eventos_conflito}")
                else:
                    # Adicionar ao Google Calendar
                    if link_evento:
                        calendar_success = add_to_calendar(nome, datetime_inicio, link_evento)
                    
                    # Adicionar ao DataFrame
                    novo_lancamento = pd.DataFrame({
                        'Nome do Evento': [nome],
                        'Data do Evento': [datetime_inicio],
                        'Data de Fim': [datetime_fim],
                        'Link Evento': [link_evento],
                        'Andamento': [andamento],
                        'Temperatura': [temperatura],
                        'Link do Grupo': [link_grupo],
                        'Período': [periodo]
                    })
                    
                    st.session_state.data = pd.concat([st.session_state.data, novo_lancamento], ignore_index=True)
                    save_data_to_csv()
                    st.success("Lançamento adicionado com sucesso!")
                    if link_evento and calendar_success:
                        st.success("Evento adicionado ao Google Calendar!")
            else:
                st.error("Por favor, corrija as datas antes de adicionar o evento.")

# Página Visualizar Lançamentos
elif selected == "Visualizar Lançamentos":
    st.markdown('<h1 class="big-title">📋 Visualizar Lançamentos</h1>', unsafe_allow_html=True)
    
    # Campo de busca em container próprio
    with st.container():
        busca = st.text_input("🔍 Buscar lançamento", placeholder="Digite o nome ou palavra-chave...")
    
    # Filtros em container próprio com espaçamento
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("### 🔍 Filtros")
        
        # Primeira linha de filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_andamento = st.multiselect(
                "Status",
                options=["Não começou", "Em andamento", "Finalizado"]
            )
        with col2:
            filtro_temperatura = st.multiselect(
                "Temperatura",
                options=["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"]
            )
        
        # Segunda linha de filtros
        st.markdown("<br>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            data_inicio_filtro = st.date_input(
                "Data Inicial",
                value=None,
                key="data_inicio_filtro"
            )
        with col4:
            data_fim_filtro = st.date_input(
                "Data Final",
                value=None,
                key="data_fim_filtro"
            )
    
    # Adicionar divisor após os filtros
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Aplicar filtros e busca
    df_filtrado = st.session_state.data.copy()
    
    # Aplicar busca
    if busca:
        df_filtrado = df_filtrado[
            df_filtrado['Nome do Evento'].str.contains(busca, case=False, na=False) |
            df_filtrado['Andamento'].str.contains(busca, case=False, na=False) |
            df_filtrado['Período'].str.contains(busca, case=False, na=False)
        ]
    
    if filtro_andamento:
        df_filtrado = df_filtrado[df_filtrado['Andamento'].isin(filtro_andamento)]
    
    if filtro_temperatura:
        df_filtrado['Temperatura_Label'] = df_filtrado['Temperatura'].apply(temperatura_to_emoji)
        df_filtrado = df_filtrado[df_filtrado['Temperatura_Label'].isin(filtro_temperatura)]
    
    # Atualizar o filtro de data
    if data_inicio_filtro and data_fim_filtro:
        if data_inicio_filtro <= data_fim_filtro:
            df_filtrado = df_filtrado[
                (df_filtrado['Data do Evento'].dt.date >= data_inicio_filtro) &
                (df_filtrado['Data de Fim'].dt.date <= data_fim_filtro)
            ]
        else:
            st.error("A data inicial deve ser menor ou igual à data final!")
    elif data_inicio_filtro:
        df_filtrado = df_filtrado[df_filtrado['Data do Evento'].dt.date >= data_inicio_filtro]
    elif data_fim_filtro:
        df_filtrado = df_filtrado[df_filtrado['Data de Fim'].dt.date <= data_fim_filtro]
    
    # Adicionar coluna de temperatura com emojis
    df_filtrado['Temperatura_Display'] = df_filtrado['Temperatura'].apply(temperatura_to_emoji)
    
    # Exibir contagem de resultados
    total_resultados = len(df_filtrado)
    st.markdown(f"### Total de lançamentos encontrados: {total_resultados}")
    
    # Exibir dados com botões de edição
    if not df_filtrado.empty:
        for idx, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div style="
                background-color: #111111;
                padding: 15px;
                border-radius: 4px;
                margin: 15px 0;
                border-left: 3px solid #ff3333;
            ">
                <h2 style="
                    margin: 0;
                    color: #ffffff;
                    font-size: 1.8em;
                    font-weight: 500;
                ">{row["Nome do Evento"]}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Ver Detalhes", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background-color: #2b2b2b;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 10px 0;
                        border-left: 3px solid #4CAF50;
                    ">
                        <p style="margin: 0;"><strong>Período:</strong> {row['Período']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write(f"**Status:** {row['Andamento']}")
                    st.write(f"**Temperatura:** {temperatura_to_emoji(row['Temperatura'])}")
                    if pd.notna(row['Link Evento']):
                        st.markdown(f"[🔗 Link do Evento]({row['Link Evento']})")
                    if pd.notna(row['Link do Grupo']):
                        st.markdown(f"[👥 Link do Grupo]({row['Link do Grupo']})")
                
                with col2:
                    if st.button("✏️ Editar", key=f"edit_{idx}"):
                        st.session_state.editing = True
                        st.session_state.edit_index = idx
                    
                    if st.button("🗑️ Excluir", key=f"delete_{idx}"):
                        st.session_state.data = st.session_state.data.drop(idx)
                        save_data_to_csv()
                        st.rerun()
                
                # Modal de edição
                if st.session_state.editing and st.session_state.edit_index == idx:
                    with st.form(key=f"edit_form_{idx}"):
                        st.subheader("Editar Lançamento")
                        
                        nome_edit = st.text_input("Nome do Evento", value=row['Nome do Evento'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### Data de Início")
                            data_inicio_edit = st.date_input("Data", value=pd.to_datetime(row['Data do Evento']).date(), key=f"data_inicio_edit_{idx}")
                            hora_inicio_edit = st.time_input("Hora", value=pd.to_datetime(row['Data do Evento']).time(), key=f"hora_inicio_edit_{idx}")
                        
                        with col2:
                            st.markdown("### Data de Fim")
                            data_fim_edit = st.date_input("Data", value=pd.to_datetime(row['Data de Fim']).date(), key=f"data_fim_edit_{idx}")
                            hora_fim_edit = st.time_input("Hora", value=pd.to_datetime(row['Data de Fim']).time(), key=f"hora_fim_edit_{idx}")
                        
                        datetime_inicio_edit = datetime.combine(data_inicio_edit, hora_inicio_edit)
                        datetime_fim_edit = datetime.combine(data_fim_edit, hora_fim_edit)
                        
                        periodo_edit = f"{data_inicio_edit.strftime('%d/%m/%Y')} {hora_inicio_edit.strftime('%H')}h - {data_fim_edit.strftime('%d/%m/%Y')} {hora_fim_edit.strftime('%H')}h"
                        
                        link_evento_edit = st.text_input("Link do Evento", value=row['Link Evento'] if pd.notna(row['Link Evento']) else "")
                        andamento_edit = st.selectbox("Andamento", ["Não começou", "Em andamento", "Finalizado"], index=["Não começou", "Em andamento", "Finalizado"].index(row['Andamento']))
                        temperatura_edit = emoji_to_temperatura(
                            st.selectbox("Temperatura", 
                                       ["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"],
                                       index=["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"].index(temperatura_to_emoji(row['Temperatura'])))
                        )
                        link_grupo_edit = st.text_input("Link do Grupo", value=row['Link do Grupo'] if pd.notna(row['Link do Grupo']) else "")
                        
                        # Botões do formulário
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Salvar"):
                                if datetime_fim_edit >= datetime_inicio_edit:
                                    st.session_state.data.at[idx, 'Nome do Evento'] = nome_edit
                                    st.session_state.data.at[idx, 'Data do Evento'] = datetime_inicio_edit
                                    st.session_state.data.at[idx, 'Data de Fim'] = datetime_fim_edit
                                    st.session_state.data.at[idx, 'Link Evento'] = link_evento_edit
                                    st.session_state.data.at[idx, 'Andamento'] = andamento_edit
                                    st.session_state.data.at[idx, 'Temperatura'] = temperatura_edit
                                    st.session_state.data.at[idx, 'Link do Grupo'] = link_grupo_edit
                                    st.session_state.data.at[idx, 'Período'] = periodo_edit
                                    
                                    save_data_to_csv()
                                    st.session_state.editing = False
                                    st.session_state.edit_index = None
                                    st.rerun()
                                else:
                                    st.error("A data de fim não pode ser anterior à data de início!")
                        
                        with col2:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.editing = False
                                st.session_state.edit_index = None
                                st.rerun()
    else:
        st.info("Nenhum lançamento encontrado com os filtros selecionados.")

# Adicionar nova seção para Tabela
elif selected == "Tabela":
    st.markdown('<h1 class="big-title">📊 Visualização em Tabela</h1>', unsafe_allow_html=True)
    
    # Filtros simples
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.multiselect(
            "Status",
            options=["Não começou", "Em andamento", "Finalizado"]
        )
    with col2:
        filtro_temp = st.multiselect(
            "Temperatura",
            options=["❄️ FRIO", "🙃 MORNO", "🔥 QUENTE"]
        )
    
    # Busca
    busca = st.text_input("🔍 Buscar", placeholder="Digite para filtrar...")
    
    # Filtrar dados
    df_tabela = st.session_state.data.copy()
    
    if busca:
        df_tabela = df_tabela[
            df_tabela['Nome do Evento'].str.contains(busca, case=False, na=False) |
            df_tabela['Período'].str.contains(busca, case=False, na=False)
        ]
    
    if filtro_status:
        df_tabela = df_tabela[df_tabela['Andamento'].isin(filtro_status)]
    
    if filtro_temp:
        df_tabela['Temperatura_Label'] = df_tabela['Temperatura'].apply(temperatura_to_emoji)
        df_tabela = df_tabela[df_tabela['Temperatura_Label'].isin(filtro_temp)]
    
    # Preparar dados para exibição
    df_display = df_tabela[['Nome do Evento', 'Período', 'Andamento', 'Temperatura']].copy()
    df_display['Temperatura'] = df_display['Temperatura'].apply(temperatura_to_emoji)
    
    # Exibir tabela
    st.dataframe(
        df_display,
        column_config={
            "Nome do Evento": "Evento",
            "Temperatura": "🌡️",
        },
        hide_index=True,
        use_container_width=True
    ) 