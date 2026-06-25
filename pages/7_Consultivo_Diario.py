import streamlit as st
import pandas as pd
import os
import calendar
import unicodedata
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- CSS E ESTILOS ---
st.markdown("""<style>
    .topo-container { background: #003366; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 20px; font-weight: 900; color: #333; text-transform: uppercase; margin-bottom: 10px; }
    .num-base { font-size: 70px; font-weight: 900; color: #111; line-height: 1; }
    
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px; }
    .sup-name { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase; }
    .badge-acumulado { background: #e8f5e9; color: #2e7d32; padding: 8px 16px; border-radius: 8px; font-size: 16px; font-weight: bold; border: 1px solid #a5d6a7; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
    .falta-box { border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #eee; background-color: #f9f9f9; }
    .falta-label { font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; color: #666; }
    .falta-value { font-size: 45px; font-weight: 900; color: #003366; line-height: 1; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="topo-container"><h1>PERFORMANCE CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)

# --- CONFIGURAÇÕES GERAIS ---
ARQUIVO_CONSULTIVO = os.path.join(os.getcwd(), "consultivo_sincronizado.csv")
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

def obter_nome_visual(n):
    n = str(n).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    if 'NELSON' in n: return "NELSON"
    if 'ALAN' in n: return "ALAN"
    return n.split()[0]

# --- LÓGICA DE PROCESSAMENTO ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        # Carrega o arquivo dinamicamente
        df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).upper().strip().replace(' ', '_') for c in df.columns]
        
        # Limpa BASE e SUPERVISOR
        col_base = next((c for c in df.columns if 'BASE' in c), None)
        col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
        
        df['BASE_CLEAN'] = df[col_base].fillna('N/D').apply(limpar_texto) if col_base else 'N/D'
        df['SUP_CLEAN'] = df[col_sup].fillna('#N/D').apply(limpar_texto) if col_sup else ''
        
        # Localiza dinamicamente a coluna de Quantidade
        col_qtd = next((c for c in df.columns if 'QTD' in c and 'PRODUT' in c), None)
        df['QTD_CALC'] = pd.to_numeric(df[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0) if col_qtd else 0

        # Filtra apenas os supervisores conhecidos
        def classificar_sup(row):
            for oficial in SUPERVISORES_ORDENADOS:
                if limpar_texto(oficial.split()[0]) in row: return oficial
            return "DESCARTADO"
        
        df['SUP_FINAL'] = df['SUP_CLEAN'].apply(classificar_sup)
        df_cards = df[df['SUP_FINAL'] != 'DESCARTADO'].copy()

        # 🔥 TRATAMENTO DE DATA INFALÍVEL 🔥
        col_data = next((c for c in df_cards.columns if 'DATA' in c), None)
        hoje_real = (datetime.utcnow() - timedelta(hours=3)).date()
        
        if col_data:
            # Converte a coluna para data do Pandas
            df_cards['DATA_DT'] = pd.to_datetime(df_cards[col_data].astype(str).str.strip(), dayfirst=True, errors='coerce')
            
            # Descobre a maior data válida (que não seja data errada do futuro)
            df_valid_dates = df_cards.dropna(subset=['DATA_DT'])
            if not df_valid_dates.empty:
                df_passado = df_valid_dates[df_valid_dates['DATA_DT'].dt.date <= hoje_real]
                if not df_passado.empty:
                    data_ref = df_passado['DATA_DT'].max().date()
                else:
                    data_ref = df_valid_dates['DATA_DT'].max().date() 
            else:
                data_ref = hoje_real
            
            # Compara datas e não textos
            df_hoje = df_cards[df_cards['DATA_DT'].dt.date == data_ref].copy()
            hoje_str = data_ref.strftime('%d/%m/%Y')
            
            # Aviso se a planilha não foi atualizada para hoje
            if data_ref != hoje_real:
                st.info(f"⏳ **Aviso:** O painel não encontrou dados para hoje ({hoje_real.strftime('%d/%m/%Y')}). Exibindo o último dia disponível: **{hoje_str}**")
        else:
            data_ref = hoje_real
            hoje_str = data_ref.strftime('%d/%m/%Y')
            df_hoje = df_cards.copy()

        # Cálculo de dias úteis restantes no mês atual
        _, num_dias = calendar.monthrange(data_ref.year, data_ref.month)
        dias_restantes = sum(1 for d in range(data_ref.day, num_dias + 1) if calendar.weekday(data_ref.year, data_ref.month, d) != 6)
        if dias_restantes == 0: dias_restantes = 1
        
        st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
            <span style="font-size: 24px; font-weight: bold; color: #555;">Resultados de {hoje_str} - Dias úteis restantes no mês: </span>
            <span style="font-size: 32px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
        </div>''', unsafe_allow_html=True)

        # Cálculos globais para os cards superiores
        total_hoje_abc = df_hoje[df_hoje['BASE_CLEAN'] == 'ABC']['QTD_CALC'].sum()
        total_hoje_sp  = df_hoje[df_hoje['BASE_CLEAN'] == 'SP']['QTD_CALC'].sum()

        meta_dia_base_abc = sum([round(max(0, 350 - df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()) / dias_restantes, 1) for sup in SUPS_ABC])
        meta_dia_base_sp = sum([round(max(0, 350 - df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()) / dias_restantes, 1) for sup in SUPS_SP])

        # Renderização das Colunas
        col_abc, col_sp = st.columns(2)
        
        def renderizar_base(base_nome, coluna_st, sups_lista, meta_geral, total_hoje):
            with coluna_st:
                classe_box = "box-base" if base_nome == "ABC" else "box-base-sp"
                cor_texto = "#2e7d32" if base_nome == "ABC" else "#00695c"
                icone_base = "🏢" if base_nome == "ABC" else "🏙️"
                
                # Card Total da Base
                st.markdown(f'''<div class="{classe_box}">
                    <div class="nome-base" style="color: {cor_texto};">{icone_base} BASE {base_nome} HOJE (Meta Diária: {round(meta_geral, 1)})</div>
                    <div class="num-base">{int(total_hoje)}</div>
                </div>''', unsafe_allow_html=True)
                
                # Cards Individuais
                for sup in sups_lista:
                    qtd_mes = df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()
                    qtd_hoje = df_hoje[df_hoje['SUP_FINAL'] == sup]['QTD_CALC'].sum()
                    
                    meta_dia = round(max(0, 350 - qtd_mes) / dias_restantes, 1)
                    falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)

                    st.markdown(f'''
                    <div class="sup-card">
                        <div class="sup-header">
                            <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                            <div class="badge-acumulado">Total Acumulado: {int(qtd_mes)}</div>
                        </div>
                        <div class="faltas-grid">
                            <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                <div class="falta-label" style="color: #2e7d32;">📦 REALIZADO HOJE</div>
                                <div class="falta-value" style="color: #1b5e20;">{int(qtd_hoje)}</div>
                            </div>
                            <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                <div class="falta-label" style="color: #c62828;">📉 FALTAM HOJE</div>
                                <div class="falta-value" style="color: #b30000;">{falta_hoje}</div>
                            </div>
                            <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                                <div class="falta-value" style="color: #b78103;">{meta_dia}</div>
                            </div>
                        </div>
                    </div>''', unsafe_allow_html=True)

        renderizar_base('ABC', col_abc, SUPS_ABC, meta_dia_base_abc, total_hoje_abc)
        renderizar_base('SP', col_sp, SUPS_SP, meta_dia_base_sp, total_hoje_sp)

    except Exception as e:
        st.error(f"Erro ao calcular os dados da planilha: {e}")
        st.info("Verifique se o formato da coluna DATA é DD/MM/AAAA e se existem produtos numéricos.")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado no sistema.")
