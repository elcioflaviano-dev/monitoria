import streamlit as st
import pandas as pd
import os
import calendar
import unicodedata
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- VARIÁVEIS GLOBAIS SEGURAS (Evita NameError) ---
icone_mudo = '<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; opacity: 0.25;"><svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="1" x2="1" y2="23"></line></svg></div>'
icone_ativo = '<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; opacity: 0.8;"><svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg></div>'

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

st.markdown('<div class="topo-container"><h1>CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)

# Exibe o ícone
st.markdown(icone_mudo, unsafe_allow_html=True)

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

# --- LÓGICA DE PROCESSAMENTO (ISOLANDO O DIA DE HOJE) ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        # Carrega o arquivo dinamicamente
        df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df_cons.columns = [str(c).upper().strip().replace(' ', '_') for c in df_cons.columns]
        
        # Limpa BASE e SUPERVISOR
        col_base = next((c for c in df_cons.columns if 'BASE' in c), None)
        col_sup = next((c for c in df_cons.columns if 'SUPERVISOR' in c), None)
        
        df_cons['BASE_CLEAN'] = df_cons[col_base].fillna('N/D').apply(limpar_texto) if col_base else 'N/D'
        df_cons['SUP_CLEAN'] = df_cons[col_sup].fillna('#N/D').apply(limpar_texto) if col_sup else ''
        
        # Localiza dinamicamente a coluna de Quantidade
        col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUT' in c), None)
        df_cons['QTD_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0) if col_qtd else 0

        # Filtra apenas os supervisores conhecidos
        def classificar_sup(row):
            for oficial in SUPERVISORES_ORDENADOS:
                if limpar_texto(oficial.split()[0]) in row: return oficial
            return "DESCARTADO"
        
        df_cons['SUP_FINAL'] = df_cons['SUP_CLEAN'].apply(classificar_sup)
        df_cards = df_cons[df_cons['SUP_FINAL'] != 'DESCARTADO'].copy()

        # 🔥 LÓGICA DE DATA: BUSCA COMO TEXTO PURO 🔥
        hoje_br = datetime.utcnow() - timedelta(hours=3)
        hoje_str_br = hoje_br.strftime('%d/%m/%Y')   # Formato BR: 26/06/2026
        hoje_str_us = hoje_br.strftime('%Y-%m-%d')   # Formato US: 2026-06-26 (Garantia)

        col_data = next((c for c in df_cards.columns if 'DATA' in c), None)
        
        if col_data:
            # Transforma a coluna da planilha em texto e corta os 10 primeiros caracteres
            df_cards['DATA_TXT'] = df_cards[col_data].astype(str).str.strip().str[:10]
            
            # Filtra onde o texto for IGUAL à data de hoje (independente de como o Excel exportou)
            mask_hoje = (df_cards['DATA_TXT'] == hoje_str_br) | (df_cards['DATA_TXT'] == hoje_str_us)
            df_hoje = df_cards[mask_hoje].copy()
        else:
            df_hoje = pd.DataFrame() 
        
        # Dias úteis restantes no mês corrente
        ano, mes = hoje_br.year, hoje_br.month
        _, num_dias = calendar.monthrange(ano, mes)
        dias_restantes = sum(1 for d in range(hoje_br.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
        if dias_restantes <= 0: dias_restantes = 1

        # Mostra o status para você saber exatamente o que o painel leu
        if df_hoje.empty:
            # Caso a planilha ainda não tenha sido atualizada hoje, mostra um aviso e as últimas datas achadas
            datas_recentes = df_cards['DATA_TXT'].unique()[:5] if col_data else "Nenhuma"
            st.warning(f"⚠️ Atenção: A planilha não possui dados lançados com a data de hoje ({hoje_str_br}). Datas encontradas no arquivo: {datas_recentes}")

        # Totais Globais Hoje
        total_hoje_abc = df_hoje[df_hoje['BASE_CLEAN'] == 'ABC']['QTD_CALC'].sum() if not df_hoje.empty else 0
        total_hoje_sp  = df_hoje[df_hoje['BASE_CLEAN'] == 'SP']['QTD_CALC'].sum() if not df_hoje.empty else 0

        # Cálculo da Meta Geral por Base
        meta_dia_base_abc = 0
        for sup in SUPS_ABC:
            qtd_m = df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()
            meta_dia_base_abc += round(max(0, 350 - qtd_m) / dias_restantes, 1)
        
        meta_dia_base_sp = 0
        for sup in SUPS_SP:
            qtd_m = df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()
            meta_dia_base_sp += round(max(0, 350 - qtd_m) / dias_restantes, 1)

        st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
            <span style="font-size: 24px; font-weight: bold; color: #555;">Consultivos de Hoje ({hoje_str_br}) - Dias úteis restantes: </span>
            <span style="font-size: 32px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
        </div>''', unsafe_allow_html=True)

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
                    # 1. Soma INTOCADA do mês (Geral)
                    qtd_mes = df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()
                    
                    # 2. Soma ISOLADA de Hoje
                    qtd_hoje = df_hoje[df_hoje['SUP_FINAL'] == sup]['QTD_CALC'].sum() if not df_hoje.empty else 0
                    
                    # 3. Fórmulas de Negócio
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
        st.info("Verifique se as colunas estão corretas.")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado no sistema.")
