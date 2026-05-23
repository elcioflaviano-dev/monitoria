import streamlit as st
import pandas as pd

# Configuração da página para modo amplo (ocupa a tela toda da TV/Monitor)
st.set_page_config(page_title="Painel de Supervisão", layout="wide")

st.title("📊 Painel Operacional de Rotas - ABC & SP")
st.write("---")
st.markdown("### Bem-vindo! Use o menu lateral para acessar os painéis.")

# Função original com cache automático para carregar os dados
@st.cache_data(ttl=60)  # Limpa o cache a cada 1 minuto se retransmitido
def carregar_dados():
    # URL oficial configurada para ler direto a exportação em CSV/Excel do seu Sheets
    URL_SHEETS = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv"
    
    # Lê os dados brutos como texto para garantir velocidade máxima sem travar
    df = pd.read_csv(URL_SHEETS, dtype=str, on_bad_lines='skip')
    
    # Remove qualquer linha completamente em branco que o Sheets possa gerar
    df = df.dropna(how='all')
    
    # Limpa espaços invisíveis dos nomes das colunas
    df.columns = [str(c).strip().replace('\xa0', ' ') for c in df.columns]
    
    # Mapeamento estrito para garantir as duas grafias das colunas (Excel e CSV)
    colunas_mapeadas = {}
    for col in df.columns:
        col_upper = col.upper()
        if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
        elif 'JANELA' in col_upper or 'INTERVALO' in col_upper or 'TEMPO' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
        elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
        elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
        elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'Recurso'
        elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo de Atividade'
            
    return df.rename(columns=colunas_mapeadas)

try:
    # Executa a carga dos dados exatamente como seu arquivo de backup fazia
    dados_carregados = carregar_dados()
    
    if dados_carregados is not None and not dados_carregados.empty:
        st.session_state['dados_rota'] = dados_carregados
        st.success("✅ Conexão estabelecida! Dados da planilha 'rota' atualizados.")
        
        # Mostra o indicador clássico de registros na tela
        total_linhas = len(st.session_state['dados_rota'])
        st.metric(label="Total de Atividades na Base", value=f"{total_linhas} registros")
    else:
        st.error("❌ A planilha online retornou sem linhas válidas para processamento.")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Sheets. Verifique o link e se as permissões de compartilhamento estão públicas.")
    st.code(e)
