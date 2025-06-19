import streamlit as st
# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Indicador de Qualidade do Ar",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globais
st.markdown("""
<style>
/* Estilo global para todos os botões */
div[data-testid="stButton"] button {
    background-color: #02ab21;
    color: white;
    font-weight: normal;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    border: none;
    font-size: 14px;
    width: auto !important;  /* Impede que os botões ocupem 100% da largura */
}

/* Estilo específico para o botão de previsão */
div[data-testid="stButton"].main-button button {
    width: 100% !important;  /* Faz apenas o botão de previsão ocupar 100% */
}

div[data-testid="stButton"] button:hover {
    background-color: #028a1a;
}

/* Estilo para cards de poluentes */
.pollutant-card {
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    padding: 10px;
    margin: 5px;
}
.pollutant-header {
    font-weight: bold;
    margin-bottom: 5px;
}

/* Estilo para inputs numéricos */
div[data-testid="stNumberInput"] input {
    font-size: 14px;
}

/* Estilo para texto do sidebar */
div[data-testid="stSidebarNav"] {
    background-color: transparent;
}
div[data-testid="stSidebarNav"] span {
    font-size: 14px;
}

/* Estilo para tabs */
div[data-testid="stHorizontalBlock"] button[data-baseweb="tab"] {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

import pandas as pd
import numpy as np
import joblib
import base64
import sys
from sklearn.preprocessing import QuantileTransformer
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import re
from streamlit_option_menu import option_menu
import io
import requests

# Função para baixar arquivos do GitHub
def download_file_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Erro ao baixar arquivo: {response.status_code}")

# URLs dos arquivos no GitHub
MODEL_URL = "https://github.com/sidnei-almeida/air_quality_indicator/raw/refs/heads/main/rf_model.joblib"
DATA_URL = "https://raw.githubusercontent.com/sidnei-almeida/air_quality_indicator/refs/heads/main/airquality.csv"
CONFIG_URL = "https://raw.githubusercontent.com/sidnei-almeida/air_quality_indicator/refs/heads/main/config.yaml"

# Carrega as configurações de autenticação
@st.cache_data
def load_config():
    try:
        # Primeiro tenta ler localmente
        with open('config.yaml') as file:
            return yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Se não encontrar localmente, baixa do GitHub
        content = download_file_from_github(CONFIG_URL)
        return yaml.load(content, Loader=SafeLoader)

config = load_config()

# Cria o objeto autenticador
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# Inicializa o estado da página de registro se não existir
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# Função para alternar entre login e registro
def toggle_register():
    st.session_state.show_register = not st.session_state.show_register

# Função para validar email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Função para registrar novo usuário
def register_new_user(username, name, email, password, password_repeat):
    if not username or not name or not email or not password:
        st.error('Todos os campos são obrigatórios')
        return False
    
    if not is_valid_email(email):
        st.error('Email inválido')
        return False
        
    if password != password_repeat:
        st.error('As senhas não coincidem')
        return False
        
    if len(password) < 6:
        st.error('A senha deve ter pelo menos 6 caracteres')
        return False
    
    # Verifica se o usuário já existe
    if 'usernames' in config['credentials']:
        if username in config['credentials']['usernames']:
            st.error('Nome de usuário já existe')
            return False
    else:
        config['credentials']['usernames'] = {}
    
    # Cria o hash da senha
    hasher = stauth.Hasher()
    hashed_password = hasher.hash(password)
    
    # Adiciona o novo usuário
    config['credentials']['usernames'][username] = {
        'email': email,
        'name': name,
        'password': hashed_password
    }
    
    # Salva no arquivo
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    return True

# Criando colunas para centralizar o conteúdo
col1, col2, col3 = st.columns([1,2,1])

with col2:
    if not st.session_state["authentication_status"]:
        if not st.session_state.show_register:
            # Mostra o formulário de login
            authenticator.login()
            
            # Adiciona o botão de registro abaixo do login
            st.write("Não tem uma conta?")
            st.button("Criar conta", on_click=toggle_register)
            
            if st.session_state["authentication_status"] == False:
                st.error('Nome de usuário/senha incorretos')
        else:
            # Mostra o formulário de registro personalizado
            st.subheader("Criar Nova Conta")
            
            # Adiciona botão para voltar ao login
            if st.button("Voltar ao login"):
                st.session_state.show_register = False
                st.rerun()
            
            with st.form("registro"):
                username = st.text_input("Nome de usuário")
                name = st.text_input("Nome completo")
                email = st.text_input("Email")
                password = st.text_input("Senha", type="password")
                password_repeat = st.text_input("Confirme a senha", type="password")
                
                if st.form_submit_button("Registrar"):
                    if register_new_user(username, name, email, password, password_repeat):
                        st.success('Usuário registrado com sucesso!')
                        st.session_state.show_register = False
                        st.rerun()

# Só mostra o conteúdo principal se estiver autenticado
if st.session_state["authentication_status"]:
    # Add the .streamlit directory to the path so we can import the banner module
    sys.path.append('.streamlit')
    try:
        from banner import add_banner
    except ImportError:
        def add_banner():
            st.markdown('<h1 class="main-header">🌬️ Indicador de Qualidade do Ar</h1>', unsafe_allow_html=True)

    # Carrega o modelo treinado
    @st.cache_resource
    def load_model():
        try:
            # Primeiro tenta carregar localmente
            return joblib.load('rf_model.joblib')
        except FileNotFoundError:
            # Se não encontrar localmente, baixa do GitHub
            content = download_file_from_github(MODEL_URL)
            with open('rf_model.joblib', 'wb') as f:
                f.write(content)
            return joblib.load('rf_model.joblib')

    model = load_model()

    # Carrega os dados de referência
    @st.cache_data
    def load_data():
        try:
            # Primeiro tenta ler localmente
            return pd.read_csv('airquality.csv')
        except FileNotFoundError:
            # Se não encontrar localmente, baixa do GitHub
            content = download_file_from_github(DATA_URL)
            return pd.read_csv(StringIO(content.decode('utf-8')))

    data = load_data()
    # Convert column names to lowercase
    data.columns = data.columns.str.lower()
    # Select numeric columns for normalization reference
    data_num = data.select_dtypes(include=['float64', 'int64'])

    def show_individual_prediction():
        st.write("Esta página permite prever o Índice de Qualidade do Ar (AQI) com base em medições individuais de poluentes.")
        
        # Inicializar histórico de previsões na sessão se não existir
        if 'prediction_history' not in st.session_state:
            st.session_state.prediction_history = []

        # Criar tabs para input e histórico
        tab1, tab2 = st.tabs(["📊 Nova Previsão", "📜 Histórico"])

        with tab1:
            # Criar containers para organizar o layout
            input_container = st.container()
            result_container = st.container()

            with input_container:
                # Definir limites e valores de referência para cada poluente
                pollutant_limits = {
                    'co': {'min': 0.0, 'max': 1000.0, 'ref': 290.0, 'unit': 'μg/m³'},
                    'no2': {'min': 0.0, 'max': 100.0, 'ref': 25.0, 'unit': 'μg/m³'},
                    'so2': {'min': 0.0, 'max': 50.0, 'ref': 1.0, 'unit': 'μg/m³'},
                    'o3': {'min': 0.0, 'max': 100.0, 'ref': 25.0, 'unit': 'μg/m³'},
                    'pm2.5': {'min': 0.0, 'max': 100.0, 'ref': 10.0, 'unit': 'μg/m³'},
                    'pm10': {'min': 0.0, 'max': 150.0, 'ref': 15.0, 'unit': 'μg/m³'}
                }

                # Criar layout com três colunas
                col1, col2 = st.columns(2)

                # Dicionário para armazenar os valores dos inputs
                input_values = {}

                with col1:
                    st.subheader("Poluentes Primários")
                    for pollutant in ['co', 'no2', 'so2']:
                        with st.container():
                            st.markdown(f"""
                            <div class="pollutant-card">
                            <div class="pollutant-header">{pollutant.upper()}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            input_values[pollutant] = st.number_input(
                                f'{pollutant.upper()} ({pollutant_limits[pollutant]["unit"]})',
                                min_value=pollutant_limits[pollutant]['min'],
                                max_value=pollutant_limits[pollutant]['max'],
                                value=float(pollutant_limits[pollutant]['ref']),
                                step=0.1,
                                help=get_pollutant_description(pollutant)
                            )

                with col2:
                    st.subheader("Poluentes Secundários")
                    for pollutant in ['o3', 'pm2.5', 'pm10']:
                        with st.container():
                            st.markdown(f"""
                            <div class="pollutant-card">
                            <div class="pollutant-header">{pollutant.upper()}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            input_values[pollutant] = st.number_input(
                                f'{pollutant.upper()} ({pollutant_limits[pollutant]["unit"]})',
                                min_value=pollutant_limits[pollutant]['min'],
                                max_value=pollutant_limits[pollutant]['max'],
                                value=float(pollutant_limits[pollutant]['ref']),
                                step=0.1,
                                help=get_pollutant_description(pollutant)
                            )

                # Botão de previsão com classe específica
                button_container = st.container()
                with button_container:
                    st.markdown('<div class="main-button">', unsafe_allow_html=True)
                    predict_button = st.button('Realizar Previsão', use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if predict_button:
                    with st.spinner('Processando dados...'):
                        # Criar DataFrame com os valores de entrada
                        input_data = pd.DataFrame({
                            'co': [input_values['co']],
                            'no2': [input_values['no2']],
                            'so2': [input_values['so2']],
                            'o3': [input_values['o3']],
                            'pm2.5': [input_values['pm2.5']],
                            'pm10': [input_values['pm10']]
                        })

                        # Normalizar dados
                        qt = QuantileTransformer(output_distribution='normal')
                        qt.fit(data_num[['co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']])
                        input_normalized = pd.DataFrame(
                            qt.transform(input_data),
                            columns=input_data.columns
                        )

                        # Fazer previsão
                        prediction = model.predict(input_normalized)
                        
                        # Adicionar ao histórico
                        st.session_state.prediction_history.append({
                            'timestamp': datetime.now(),
                            'inputs': input_values.copy(),
                            'prediction': prediction[0]
                        })

                        # Mostrar resultado
                        with result_container:
                            show_prediction_result(prediction[0])
                            
                            # Adicionar gráfico comparativo
                            st.subheader("Comparação com Valores de Referência")
                            
                            # Preparar dados para o gráfico
                            comparison_data = {
                                'Atual': list(input_values.values()),
                                'Referência': [pollutant_limits[p]['ref'] for p in input_values.keys()]
                            }
                            
                            # Criar gráfico de barras
                            fig = go.Figure()
                            
                            # Adicionar barras para valores atuais
                            fig.add_trace(go.Bar(
                                name='Medição Atual',
                                x=list(input_values.keys()),
                                y=comparison_data['Atual'],
                                marker_color='#02ab21'
                            ))
                            
                            # Adicionar barras para valores de referência
                            fig.add_trace(go.Bar(
                                name='Valor de Referência',
                                x=list(input_values.keys()),
                                y=comparison_data['Referência'],
                                marker_color='rgba(2, 171, 33, 0.3)'
                            ))
                            
                            # Atualizar layout
                            fig.update_layout(
                                title="Comparação com Valores de Referência",
                                xaxis_title="Poluentes",
                                yaxis_title="Concentração (μg/m³)",
                                barmode='group',
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if st.session_state.prediction_history:
                st.subheader("Histórico de Previsões")
                
                # Criar DataFrame com histórico
                history_data = []
                for pred in st.session_state.prediction_history:
                    row = {
                        'Data/Hora': pred['timestamp'].strftime('%d/%m/%Y %H:%M:%S'),
                        'AQI Previsto': f"{pred['prediction']:.2f}"
                    }
                    row.update({k.upper(): f"{v:.2f}" for k, v in pred['inputs'].items()})
                    history_data.append(row)
                
                history_df = pd.DataFrame(history_data)
                
                # Mostrar tabela com histórico
                st.dataframe(
                    history_df.style.background_gradient(subset=['AQI Previsto'], cmap='YlOrRd'),
                    use_container_width=True
                )
                
                # Adicionar gráfico de evolução do AQI
                fig = px.line(
                    x=[pred['timestamp'] for pred in st.session_state.prediction_history],
                    y=[pred['prediction'] for pred in st.session_state.prediction_history],
                    title="Evolução do AQI nas Previsões",
                    labels={'x': 'Data/Hora', 'y': 'AQI Previsto'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Botão para limpar histórico
                if st.button('Limpar Histórico'):
                    st.session_state.prediction_history = []
                    st.rerun()
            else:
                st.info("Nenhuma previsão realizada ainda.")

    def get_pollutant_description(pollutant):
        """Retorna a descrição de cada poluente."""
        descriptions = {
            'co': "Monóxido de carbono (CO) é um gás incolor e inodoro emitido de processos de combustão.",
            'no2': "Dióxido de nitrogênio (NO₂) é um gás marrom-avermelhado, principalmente de emissões veiculares.",
            'so2': "Dióxido de enxofre (SO₂) é um gás incolor com odor forte, principalmente da queima de combustíveis fósseis.",
            'o3': "Ozônio (O₃) é um gás composto por três átomos de oxigênio, formado por reação química entre óxidos de nitrogênio e compostos orgânicos voláteis.",
            'pm2.5': "PM2.5 são partículas finas inaláveis com diâmetros geralmente de 2,5 micrômetros ou menos.",
            'pm10': "PM10 são partículas inaláveis com diâmetros geralmente de 10 micrômetros ou menos."
        }
        return descriptions.get(pollutant, "")

    def show_batch_prediction():
        st.write("Esta página permite fazer previsões em lote do Índice de Qualidade do Ar (AQI) para múltiplas medições.")
        
        # Criar template com valores de exemplo
        template_data = pd.DataFrame({
            'co': [290.0, 300.0, 280.0],
            'no2': [25.0, 30.0, 20.0],
            'so2': [1.0, 1.5, 0.8],
            'o3': [25.0, 28.0, 22.0],
            'pm2.5': [10.0, 12.0, 8.0],
            'pm10': [15.0, 18.0, 13.0]
        })
        
        # Criar abas para organizar o conteúdo
        tab1, tab2 = st.tabs(["📥 Upload e Previsão", "📋 Instruções"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div style='border: 1px solid #e0e0e0; border-radius: 5px; padding: 15px; margin-bottom: 20px;'>
                    <h3 style='margin-top: 0;'>📤 Upload de Arquivo</h3>
                    <p>Faça upload de um arquivo CSV com as medições dos poluentes.</p>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
            
            with col2:
                st.markdown("""
                <div style='border: 1px solid #e0e0e0; border-radius: 5px; padding: 15px; margin-bottom: 20px;'>
                    <h3 style='margin-top: 0;'>📄 Template</h3>
                    <p>Baixe o template com exemplos.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Opções de download do template
                format_option = st.selectbox(
                    "Formato do template:",
                    ["CSV", "Excel"],
                    key="template_format"
                )
                
                if format_option == "CSV":
                    st.download_button(
                        label="📥 Download Template CSV",
                        data=template_data.to_csv(index=False),
                        file_name="template.csv",
                        mime="text/csv"
                    )
                else:
                    # Criar buffer para arquivo Excel
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        template_data.to_excel(writer, sheet_name='Template', index=False)
                        # Ajustar largura das colunas
                        worksheet = writer.sheets['Template']
                        for i, col in enumerate(template_data.columns):
                            worksheet.set_column(i, i, 15)
                    
                    st.download_button(
                        label="📥 Download Template Excel",
                        data=buffer.getvalue(),
                        file_name="template.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            if uploaded_file is not None:
                try:
                    # Tentar ler o arquivo
                    input_df = pd.read_csv(uploaded_file)
                    required_columns = ['co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']
                    
                    # Verificar colunas
                    missing_cols = [col for col in required_columns if col not in input_df.columns]
                    if missing_cols:
                        st.error(f"❌ Colunas ausentes no arquivo: {', '.join(missing_cols)}")
                        return
                    
                    # Verificar tipos de dados e valores
                    invalid_rows = []
                    for idx, row in input_df.iterrows():
                        try:
                            for col in required_columns:
                                # Converter para float e verificar se é negativo
                                val = float(row[col])
                                if val < 0:
                                    invalid_rows.append(idx + 1)
                                    break
                        except (ValueError, TypeError):
                            invalid_rows.append(idx + 1)
                            break
                    
                    if invalid_rows:
                        st.error(f"❌ Linhas com valores inválidos: {', '.join(map(str, invalid_rows))}")
                        return
                    
                    # Preview dos dados com estilo
                    st.markdown("### 📊 Preview dos Dados")
                    
                    # Adicionar toggle para mostrar estatísticas
                    show_stats = st.checkbox("Mostrar estatísticas básicas")
                    if show_stats:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 📈 Estatísticas Gerais")
                            stats = input_df.describe()
                            st.dataframe(stats.style.format("{:.2f}"))
                        with col2:
                            st.markdown("#### 🔍 Informações do Dataset")
                            st.write(f"- Total de registros: {len(input_df)}")
                            st.write(f"- Memória utilizada: {input_df.memory_usage().sum() / 1024:.2f} KB")
                            st.write("- Tipos de dados:")
                            for col in input_df.columns:
                                st.write(f"  - {col}: {input_df[col].dtype}")
                    
                    # Preview da tabela com scroll
                    st.markdown("#### 📋 Dados Carregados")
                    st.dataframe(
                        input_df.head(10).style.background_gradient(cmap='YlOrRd', subset=required_columns),
                        use_container_width=True
                    )
                    
                    # Container para os botões de ação
                    col1, col2, col3 = st.columns([1,1,1])
                    with col2:
                        st.markdown('<div class="main-button">', unsafe_allow_html=True)
                        predict_button = st.button("🎯 Realizar Previsões", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Mover a lógica de previsão para fora das colunas
                    if predict_button:
                        # Criar barra de progresso
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        try:
                            # Normalizar dados
                            status_text.text("Normalizando dados...")
                            qt = QuantileTransformer(output_distribution='normal')
                            qt.fit(data_num[required_columns])
                            input_normalized = pd.DataFrame(
                                qt.transform(input_df[required_columns]),
                                columns=required_columns
                            )
                            progress_bar.progress(30)
                            
                            # Fazer previsões
                            status_text.text("Realizando previsões...")
                            predictions = model.predict(input_normalized)
                            progress_bar.progress(60)
                            
                            # Preparar resultados
                            status_text.text("Preparando resultados...")
                            results_df = input_df.copy()
                            results_df['aqi_prediction'] = predictions
                            progress_bar.progress(90)
                            
                            # Mostrar resultados
                            st.success("✅ Previsões realizadas com sucesso!")
                            progress_bar.progress(100)
                            status_text.empty()
                            
                            # Criar container para resultados usando toda a largura
                            st.markdown("### 📊 Resultados das Previsões")
                            
                            # Tabs para diferentes visualizações dos resultados
                            result_tab1, result_tab2, result_tab3 = st.tabs([
                                "📊 Resultados", 
                                "📈 Visualizações",
                                "📥 Exportar"
                            ])
                            
                            with result_tab1:
                                # Estilizar e mostrar o dataframe
                                st.dataframe(
                                    results_df.style
                                    .format({
                                        'aqi_prediction': '{:.2f}',
                                        'co': '{:.2f}',
                                        'no2': '{:.2f}',
                                        'so2': '{:.2f}',
                                        'o3': '{:.2f}',
                                        'pm2.5': '{:.2f}',
                                        'pm10': '{:.2f}'
                                    })
                                    .background_gradient(
                                        subset=['aqi_prediction'],
                                        cmap='YlOrRd'
                                    ),
                                    use_container_width=True
                                )
                                
                                # Adicionar estatísticas resumidas em colunas que ocupam toda a largura
                                st.markdown("#### 📊 Estatísticas Resumidas")
                                metric_cols = st.columns(4)
                                
                                with metric_cols[0]:
                                    st.metric(
                                        "AQI Médio",
                                        f"{results_df['aqi_prediction'].mean():.2f}",
                                        f"{results_df['aqi_prediction'].std():.2f} σ"
                                    )
                                
                                with metric_cols[1]:
                                    st.metric(
                                        "AQI Máximo",
                                        f"{results_df['aqi_prediction'].max():.2f}",
                                        f"Linha {results_df['aqi_prediction'].idxmax() + 1}"
                                    )
                                
                                with metric_cols[2]:
                                    st.metric(
                                        "AQI Mínimo",
                                        f"{results_df['aqi_prediction'].min():.2f}",
                                        f"Linha {results_df['aqi_prediction'].idxmin() + 1}"
                                    )
                                
                                with metric_cols[3]:
                                    n_critical = len(results_df[results_df['aqi_prediction'] > 150])
                                    st.metric(
                                        "Registros Críticos",
                                        n_critical,
                                        f"{(n_critical/len(results_df))*100:.1f}%"
                                    )

                            with result_tab2:
                                # Criar subseções para diferentes tipos de visualização
                                st.markdown("#### 📈 Distribuição do AQI")
                                dist_col1, dist_col2 = st.columns(2)
                                
                                with dist_col1:
                                    # Histograma melhorado das previsões
                                    fig_hist = px.histogram(
                                        results_df,
                                        x='aqi_prediction',
                                        nbins=30,
                                        title='Distribuição das Previsões de AQI',
                                        labels={'aqi_prediction': 'AQI Previsto', 'count': 'Frequência'},
                                        color_discrete_sequence=['#02ab21']
                                    )
                                    fig_hist.update_layout(
                                        showlegend=False,
                                        plot_bgcolor='white',
                                        title_x=0.5
                                    )
                                    st.plotly_chart(fig_hist, use_container_width=True)
                                
                                with dist_col2:
                                    # Box plot melhorado
                                    fig_box = px.box(
                                        results_df,
                                        y='aqi_prediction',
                                        title='Distribuição do AQI (Box Plot)',
                                        labels={'aqi_prediction': 'AQI Previsto'},
                                        color_discrete_sequence=['#02ab21']
                                    )
                                    fig_box.update_layout(
                                        showlegend=False,
                                        plot_bgcolor='white',
                                        title_x=0.5
                                    )
                                    st.plotly_chart(fig_box, use_container_width=True)

                                # Adicionar seção de análise temporal se houver coluna de data
                                if 'date' in results_df.columns:
                                    st.markdown("#### 📅 Análise Temporal")
                                    # Gráfico de linha do AQI ao longo do tempo
                                    fig_time = px.line(
                                        results_df,
                                        x='date',
                                        y='aqi_prediction',
                                        title='Evolução do AQI ao Longo do Tempo',
                                        labels={
                                            'date': 'Data',
                                            'aqi_prediction': 'AQI Previsto'
                                        }
                                    )
                                    fig_time.update_layout(
                                        plot_bgcolor='white',
                                        title_x=0.5
                                    )
                                    st.plotly_chart(fig_time, use_container_width=True)

                                # Análise de Correlação
                                st.markdown("#### 🔄 Correlação entre Variáveis")
                                
                                # Heatmap de correlação
                                corr_matrix = results_df[['aqi_prediction', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].corr()
                                fig_corr = px.imshow(
                                    corr_matrix,
                                    labels=dict(color="Correlação"),
                                    color_continuous_scale='RdBu',
                                    aspect='auto'
                                )
                                fig_corr.update_layout(
                                    title={
                                        'text': 'Matriz de Correlação',
                                        'x': 0.5
                                    }
                                )
                                st.plotly_chart(fig_corr, use_container_width=True)

                                # Análise de Contribuição
                                st.markdown("#### 🎯 Contribuição dos Poluentes")
                                
                                # Calcular médias dos poluentes
                                pollutant_means = results_df[['co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].mean()
                                
                                # Criar gráfico de barras para médias dos poluentes
                                fig_contrib = go.Figure(data=[
                                    go.Bar(
                                        x=pollutant_means.index,
                                        y=pollutant_means.values,
                                        marker_color='#02ab21'
                                    )
                                ])
                                fig_contrib.update_layout(
                                    title={
                                        'text': 'Média dos Poluentes',
                                        'x': 0.5
                                    },
                                    xaxis_title="Poluente",
                                    yaxis_title="Concentração Média (μg/m³)",
                                    plot_bgcolor='white'
                                )
                                st.plotly_chart(fig_contrib, use_container_width=True)

                                # Adicionar insights baseados nos dados
                                st.markdown("#### 💡 Insights")
                                insights_col1, insights_col2 = st.columns(2)
                                
                                with insights_col1:
                                    # Encontrar o poluente mais correlacionado com AQI
                                    corr_with_aqi = corr_matrix['aqi_prediction'].abs()
                                    most_corr = corr_with_aqi.nlargest(2).index[1]  # Pegar o segundo maior (primeiro é o próprio AQI)
                                    st.info(f"🔍 O poluente mais correlacionado com o AQI é {most_corr.upper()} " +
                                           f"(correlação: {corr_matrix.loc['aqi_prediction', most_corr]:.2f})")
                                
                                with insights_col2:
                                    # Identificar poluente com maior variação
                                    cv = results_df[['co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].std() / results_df[['co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].mean()
                                    most_variable = cv.idxmax()
                                    st.info(f"📊 O poluente com maior variação relativa é {most_variable.upper()} " +
                                           f"(CV: {cv[most_variable]:.2f})")

                            with result_tab3:
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    # Download CSV
                                    st.download_button(
                                        label="📥 Download CSV",
                                        data=results_df.to_csv(index=False),
                                        file_name="predictions.csv",
                                        mime="text/csv"
                                    )
                                
                                with col2:
                                    # Download Excel
                                    buffer = io.BytesIO()
                                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                        results_df.to_excel(writer, sheet_name='Predictions', index=False)
                                        # Ajustar largura das colunas
                                        worksheet = writer.sheets['Predictions']
                                        for i, col in enumerate(results_df.columns):
                                            worksheet.set_column(i, i, 15)
                                    
                                    st.download_button(
                                        label="📥 Download Excel",
                                        data=buffer.getvalue(),
                                        file_name="predictions.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                
                        except Exception as e:
                            st.error(f"❌ Erro ao processar as previsões: {str(e)}")
                            progress_bar.empty()
                            status_text.empty()
                        st.markdown('</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"❌ Erro ao ler o arquivo: {str(e)}")
        
        with tab2:
            st.markdown("""
            ### 📋 Instruções de Uso
            
            1. **Preparação dos Dados**
               - Baixe o template no formato desejado (CSV ou Excel)
               - Preencha com suas medições de poluentes
               - Mantenha os nomes das colunas inalterados
            
            2. **Formato dos Dados**
               - Todas as medições devem ser números positivos
               - Use ponto (.) como separador decimal
               - Não deixe células vazias
            
            3. **Colunas Necessárias**
               - co: Monóxido de Carbono (μg/m³)
               - no2: Dióxido de Nitrogênio (μg/m³)
               - so2: Dióxido de Enxofre (μg/m³)
               - o3: Ozônio (μg/m³)
               - pm2.5: Material Particulado < 2.5μm (μg/m³)
               - pm10: Material Particulado < 10μm (μg/m³)
            
            4. **Limites Recomendados**
               - CO: 0-1000 μg/m³
               - NO₂: 0-100 μg/m³
               - SO₂: 0-50 μg/m³
               - O₃: 0-100 μg/m³
               - PM2.5: 0-100 μg/m³
               - PM10: 0-150 μg/m³
            """)

    def show_data_analysis():
        st.write("Esta página apresenta análises e insights sobre os dados históricos de qualidade do ar.")
        
        # Converter data para datetime se existir
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            
            # Adicionar filtros de data
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Data Inicial",
                    value=data['date'].min().date(),
                    min_value=data['date'].min().date(),
                    max_value=data['date'].max().date()
                )
            with col2:
                end_date = st.date_input(
                    "Data Final",
                    value=data['date'].max().date(),
                    min_value=data['date'].min().date(),
                    max_value=data['date'].max().date()
                )
            
            # Filtrar dados pelo período selecionado
            mask = (data['date'].dt.date >= start_date) & (data['date'].dt.date <= end_date)
            filtered_data = data[mask]
        else:
            filtered_data = data

        # Criar abas para diferentes tipos de análise
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Tendências Temporais",
            "🔄 Correlações",
            "📊 Distribuições",
            "📑 Estatísticas"
        ])
        
        with tab1:
            st.subheader("Tendências Temporais dos Poluentes")
            if 'date' in data.columns:
                # Seletor de poluentes para visualização
                pollutants = st.multiselect(
                    "Selecione os poluentes para visualizar:",
                    options=['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10'],
                    default=['aqi']
                )
                
                if pollutants:
                    # Criar gráfico de linha para cada poluente selecionado
                    fig = go.Figure()
                    for pollutant in pollutants:
                        fig.add_trace(go.Scatter(
                            x=filtered_data['date'],
                            y=filtered_data[pollutant],
                            name=pollutant.upper(),
                            mode='lines'
                        ))
                    
                    fig.update_layout(
                        title="Variação dos Poluentes ao Longo do Tempo",
                        xaxis_title="Data",
                        yaxis_title="Concentração (μg/m³)",
                        hovermode="x unified",
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Adicionar análise de tendência
                    st.subheader("Análise de Tendência")
                    for pollutant in pollutants:
                        media = filtered_data[pollutant].mean()
                        tendencia = filtered_data[pollutant].diff().mean()
                        st.write(f"**{pollutant.upper()}**:")
                        st.write(f"- Média: {media:.2f} μg/m³")
                        st.write(f"- Tendência: {'crescente' if tendencia > 0 else 'decrescente' if tendencia < 0 else 'estável'}")
        
        with tab2:
            st.subheader("🔄 Correlação entre Poluentes")
            
            # Matriz de correlação com heatmap interativo
            corr = filtered_data[['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].corr()
            
            # Criar heatmap com Plotly
            fig = go.Figure(data=go.Heatmap(
                z=corr,
                x=corr.columns,
                y=corr.columns,
                colorscale='RdBu',
                zmin=-1,
                zmax=1,
                text=np.round(corr, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Matriz de Correlação dos Poluentes",
                height=500,
                width=700
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Adicionar scatter plot para análise bivariada
            st.subheader("Análise Bivariada")
            col1, col2 = st.columns(2)
            with col1:
                x_var = st.selectbox("Variável X:", ['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10'])
            with col2:
                y_var = st.selectbox("Variável Y:", ['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10'], index=1)
            
            fig = px.scatter(
                filtered_data,
                x=x_var,
                y=y_var,
                trendline="ols",
                title=f"Relação entre {x_var.upper()} e {y_var.upper()}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("📊 Distribuição dos Poluentes")
            
            # Seletor de poluente
            pollutant = st.selectbox(
                "Selecione um poluente:",
                ['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma
                fig = px.histogram(
                    filtered_data,
                    x=pollutant,
                    nbins=30,
                    title=f"Distribuição de {pollutant.upper()}"
                )
                fig.update_layout(bargap=0.1)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Box plot
                fig = px.box(
                    filtered_data,
                    y=pollutant,
                    title=f"Box Plot de {pollutant.upper()}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Adicionar estatísticas descritivas
            st.subheader("Estatísticas Descritivas")
            stats = filtered_data[pollutant].describe()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Média", f"{stats['mean']:.2f}")
            col2.metric("Mediana", f"{stats['50%']:.2f}")
            col3.metric("Desvio Padrão", f"{stats['std']:.2f}")
            col4.metric("IQR", f"{stats['75%'] - stats['25%']:.2f}")
        
        with tab4:
            st.subheader("📑 Estatísticas Detalhadas")
            
            # Tabela de estatísticas com formatação
            stats_df = filtered_data[['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].describe()
            st.dataframe(
                stats_df.style.format("{:.2f}")
                .background_gradient(cmap='YlOrRd', axis=1)
            )
            
            # Adicionar informações sobre os dados
            st.subheader("Informações sobre os Dados")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Período da Análise:**")
                if 'date' in data.columns:
                    st.write(f"- Início: {filtered_data['date'].min().strftime('%d/%m/%Y')}")
                    st.write(f"- Fim: {filtered_data['date'].max().strftime('%d/%m/%Y')}")
                st.write(f"- Total de registros: {len(filtered_data)}")
            
            with col2:
                st.write("**Qualidade dos Dados:**")
                missing_data = filtered_data[['aqi', 'co', 'no2', 'so2', 'o3', 'pm2.5', 'pm10']].isnull().sum()
                for col, missing in missing_data.items():
                    if missing > 0:
                        st.write(f"- {col.upper()}: {missing} valores faltantes")
                    else:
                        st.write(f"- {col.upper()}: Dados completos")

    def show_about():
        st.header("Sobre o Projeto 🌍")
        
        st.write("""
        Este projeto foi desenvolvido com o objetivo de auxiliar na previsão e monitoramento da qualidade do ar,
        utilizando técnicas avançadas de Machine Learning.
        """)
        
        st.subheader("Como Funciona? 🤔")
        st.write("""
        O sistema utiliza um modelo Random Forest treinado com dados históricos de qualidade do ar.
        O modelo foi escolhido após comparação com diversos algoritmos, apresentando o menor erro quadrático médio (MSE).
        """)
        
        st.subheader("Recursos Disponíveis 🛠️")
        st.write("""
        - Previsão individual de AQI
        - Previsões em lote
        - Análise de dados históricos
        - Visualizações interativas
        """)
        
        st.subheader("Interpretação do AQI 📊")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("0-50: Bom")
            st.warning("51-100: Moderado")
            st.warning("101-150: Insalubre para Grupos Sensíveis")
            
        with col2:
            st.error("151-200: Insalubre")
            st.error("201-300: Muito Insalubre")
            st.error("301+: Perigoso")

    def show_prediction_result(aqi_value):
        st.header("🔍 Resultado da Previsão")
        
        # Definir categorias e limites de AQI
        categories = {
            (0, 50): ("Bom", "🟢", "#00e400"),
            (51, 100): ("Moderado", "🟡", "#ffff00"),
            (101, 150): ("Insalubre para Grupos Sensíveis", "🟠", "#ff7e00"),
            (151, 200): ("Insalubre", "🔴", "#ff0000"),
            (201, 300): ("Muito Insalubre", "🟣", "#8f3f97"),
            (301, float('inf')): ("Perigoso", "⚫", "#7e0023")
        }
        
        # Encontrar a categoria correspondente
        for (min_val, max_val), (category, emoji, color) in categories.items():
            if min_val <= aqi_value <= max_val:
                break
        
        # Criar colunas para layout
        col1, col2, col3 = st.columns([1,2,1])
        
        with col2:
            # Mostrar o valor do AQI com formatação
            st.markdown(f"""
            <div style='text-align: center; background-color: {color}; padding: 20px; border-radius: 10px;'>
                <h2 style='color: white; margin: 0;'>{emoji} AQI: {aqi_value:.1f}</h2>
                <p style='color: white; font-size: 20px; margin: 10px 0;'>{category}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recomendações baseadas na categoria
        st.subheader("🏥 Recomendações de Saúde")
        
        recommendations = {
            "Bom": [
                "Qualidade do ar satisfatória",
                "Ideal para atividades ao ar livre",
                "Continue monitorando a qualidade do ar"
            ],
            "Moderado": [
                "Pessoas muito sensíveis devem considerar reduzir exercícios prolongados ao ar livre",
                "Bom para a maioria das atividades ao ar livre",
                "Monitore se há mudanças nos sintomas respiratórios"
            ],
            "Insalubre para Grupos Sensíveis": [
                "Pessoas com problemas respiratórios devem limitar atividades ao ar livre",
                "Crianças e idosos devem reduzir esforço prolongado ao ar livre",
                "Mantenha janelas fechadas se possível"
            ],
            "Insalubre": [
                "Evite atividades ao ar livre prolongadas",
                "Use máscara ao sair",
                "Mantenha-se em ambientes fechados com ar filtrado"
            ],
            "Muito Insalubre": [
                "Evite qualquer atividade ao ar livre",
                "Use máscara apropriada se precisar sair",
                "Considere usar purificador de ar em casa"
            ],
            "Perigoso": [
                "Permaneça em ambiente interno",
                "Evite qualquer atividade física ao ar livre",
                "Procure orientação médica se sentir sintomas"
            ]
        }
        
        for rec in recommendations[category]:
            st.write(f"• {rec}")

    # Sidebar for navigation
    st.sidebar.title(f"Olá, {st.session_state['name']} 👋")
    
    # Novo menu de navegação minimalista
    with st.sidebar:
        selected = option_menu(
            menu_title=None,  # Remove o título do menu
            options=["Previsão", "Lote", "Análise", "Sobre"],  # Nomes mais curtos
            icons=['graph-up', 'file-earmark', 'bar-chart', 'info-circle'],  # Ícones mais simples
            menu_icon=None,  # Remove o ícone do menu
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#02ab21", "font-size": "16px"},  # Verde do tema, ícones menores
                "nav-link": {
                    "font-size": "14px",  # Fonte menor
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "10px",  # Padding menor
                    "--hover-color": "#e6f3e6",  # Verde muito claro no hover
                    "background-color": "transparent",
                },
                "nav-link-selected": {
                    "background-color": "#02ab21",  # Verde do tema
                    "color": "white",  # Texto branco quando selecionado
                    "font-weight": "normal"  # Remove o negrito
                },
            }
        )
        
        # Botão de logout mais discreto
        st.markdown("""
            <style>
            div[data-testid="stButton"] button {
                background-color: transparent;
                color: #02ab21;
                border: 1px solid #02ab21;
                padding: 0.25rem 0.75rem;
                font-size: 12px;
                border-radius: 4px;
            }
            div[data-testid="stButton"] button:hover {
                background-color: #02ab21;
                color: white;
                border: 1px solid #02ab21;
            }
            </style>
        """, unsafe_allow_html=True)
        authenticator.logout("Sair", "sidebar")

    # Add the banner to the top of the page
    add_banner()
    
    # Conteúdo baseado na seleção do menu
    if selected == "Previsão":  # Ajustado para corresponder aos novos nomes
        st.header("🎯 Previsão Individual")
        st.write("Faça previsões para medições individuais de poluentes.")
        show_individual_prediction()
    elif selected == "Lote":  # Ajustado para corresponder aos novos nomes
        st.header("📊 Previsão em Lote")
        st.write("Faça previsões para múltiplas medições de uma vez.")
        show_batch_prediction()
    elif selected == "Análise":  # Ajustado para corresponder aos novos nomes
        st.header("📈 Análise de Dados")
        st.write("Explore e analise os dados históricos de qualidade do ar.")
        show_data_analysis()
    else:  # Sobre
        st.header("ℹ️ Sobre o Projeto")
        st.write("Informações sobre o projeto e sua implementação.")
        show_about()
