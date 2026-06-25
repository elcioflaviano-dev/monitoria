import streamlit as st
import pandas as pd
import os
import unicodedata
from datetime import datetime, timedelta
import calendar

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- REUTILIZAÇÃO DE ESTILO ---
st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    .topo-container { background: #003366; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; text-transform: uppercase; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #f9f9f9; border: 1px solid #eee; border-radius: 6px; padding: 10px; text-align: center; }
    .falta-value { font-size: 32px; font-weight: 900; color: #003366; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="topo-container"><h1>PERFORMANCE CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)

# Lógica de processamento (Mesma do painel rotativo)
ARQUIVO_CONSULTIVO = os.path.join(os.getcwd(), "consultivo_sincronizado.csv")
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

if os.path.exists(ARQUIVO_CONSULTIVO):
    df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df_cons.columns = [str(c).upper().replace(' ', '_') for c in df_cons.columns]
    
    # Cálculos dinâmicos
    # --- AJUSTE DE DATA E CÁLCULO ---
    hoje = datetime.utcnow() - timedelta(hours=3)
    hoje_str = hoje.strftime('%d/%m/%Y')  # Formato que vamos buscar

    # Força a coluna DATA a ser reconhecida como texto puro para comparação exata
    df['DATA_STR'] = df['DATA'].astype(str).str.strip()

    # Filtra apenas o que é de hoje
    # Se o seu CSV usa 2026-06-26, ajuste aqui. Se usa 26/06/2026, a linha abaixo funciona:
    df_hoje = df[df['DATA_STR'] == hoje_str].copy()

    # Cálculo por supervisor
    qtd_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_hoje['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
    _, num_dias = calendar.monthrange(hoje.year, hoje.month)
    dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
    
    col_abc, col_sp = st.columns(2)
    
    # Função para renderizar cards
    def render_cards(base, col, superv_list):
        with col:
            st.subheader(f"BASE {base}")
            for sup in superv_list:
                # Filtragem e cálculo (Ajuste o nome da coluna QTD_PRODUTOS conforme seu CSV)
                qtd_mes = df_cons[df_cons['SUPERVISOR'].str.contains(sup.split()[0], na=False) & (df_cons['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
                meta_dia = round(max(0, 350 - qtd_mes) / max(1, dias_restantes), 1)
                
                st.markdown(f'''
                <div class="sup-card">
                    <div class="sup-name">{sup}</div>
                    <div class="faltas-grid">
                        <div class="falta-box"><div class="falta-label">Acumulado</div><div class="falta-value">{int(qtd_mes)}</div></div>
                        <div class="falta-box"><div class="falta-label">Meta Dia</div><div class="falta-value">{meta_dia}</div></div>
                    </div>
                </div>''', unsafe_allow_html=True)

    render_cards('ABC', col_abc, SUPS_ABC)
    render_cards('SP', col_sp, SUPS_SP)
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado.")
