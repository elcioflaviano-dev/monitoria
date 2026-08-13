import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import unicodedata
import pydeck as pdk

# =========================================================================
# CONFIGURAÇÕES INICIAIS DA PÁGINA
# =========================================================================
st.set_page_config(page_title="Mapas da Operação", layout="wide", initial_sidebar_state="expanded")

ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

SUPERVISORES_ORDENADOS = ["EDSON MARCO", "MAICON", "NELSON"]

# --- FUNÇÕES GLOBAIS E CSS ---
def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 80px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    /* Ajuste do container para esticar o mapa */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 98% !important; }
    
    /* ESCONDE A BARRA DE ROLAGEM MAS MANTÉM A TELA INTEIRA INTACTA */
    ::-webkit-scrollbar { display: none !important; }
    html, body { -ms-overflow-style: none !important; scrollbar-width: none !important; }

    /* ESTILOS DE INTERFACE E CABEÇALHO AZUL */
    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer { display: none !important; visibility: hidden !important; }
    
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: auto 1fr auto; align-items: center; margin-bottom: 10px; height: 80px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; white-space: nowrap; width: 100%; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #003366; background: #fff; font-size: 16px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; transition: 0.3s;}
    .botao-home:hover { background: #ff9800; color: #fff; border-color: #ff9800; }

    /* FORÇAR ALTURA DO MAPA PYDECK - VISÃO DE COMANDO */
    [data-testid="stDeckGlJsonChart"] {
        height: 80vh !important;
        min-height: 650px !important;
        border-radius: 12px;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.15);
    }
</style>""", unsafe_allow_html=True)

# =========================================================================
# FUNÇÕES DE LIMPEZA E PADRONIZAÇÃO
# =========================================================================
def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

def padronizar_status(val):
    val_clean = limpar_texto(str(val))
    if 'CANCEL' in val_clean or 'SUSP' in val_clean:
        return 'Cancelado'
    if 'NE' in val_clean or 'NAO CONCLUIDO' in val_clean or 'QUEBRA' in val_clean or 'O.S NE' in val_clean: 
        return 'O.S NE'
    if 'PRODUTIVO' in val_clean or 'CONCL' in val_clean or 'EXEC' in val_clean: 
        return 'Produtivo'
    return 'Em aberto'

def class_sup_mapa(row, col_sup):
    sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
    for oficial in SUPERVISORES_ORDENADOS:
        if oficial in sup: return oficial
    return "DESCARTADO"

def cor_sup_rgb(sup):
    if sup == "MAICON": return [255, 20, 147]      # Rosa
    if sup == "NELSON": return [0, 128, 0]         # Verde
    if sup == "EDSON MARCO": return [128, 0, 128]  # Roxo
    return [0, 0, 0]

# =========================================================================
# BARRA LATERAL (MENU DE NAVEGAÇÃO)
# =========================================================================
st.sidebar.markdown("## 📍 Comandos do Mapa")
st.sidebar.markdown("Escolha a visão para rastrear os **contratos pendentes** da operação.")
st.sidebar.markdown("---")

visao_selecionada = st.sidebar.radio(
    "SELECIONE A VISÃO:",
    ["🌍 MAPA GERAL DA OPERAÇÃO", 
     "🟣 MAPA - EDSON MARCO", 
     "💗 MAPA - MAICON", 
     "🟢 MAPA - NELSON"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("⚠️ Apenas **Técnicos do ABC** com contratos no status **Em Aberto/Pendente** são exibidos no mapa.")

# =========================================================================
# CABEÇALHO AZUL DINÂMICO
# =========================================================================
titulo_tela = visao_selecionada.split(" - ")[-1] if "-" in visao_selecionada else visao_selecionada.replace("🌍 ", "")

st.markdown(f'''
<div class="topo-container">
    <div class="topo-esquerda">{logo_html}</div>
    <div class="topo-centro">{titulo_tela}</div>
    <div class="topo-direita"><a href="/" class="botao-home">🏠 VOLTAR</a></div>
</div>
''', unsafe_allow_html=True)

# =========================================================================
# PROCESSAMENTO DOS DADOS E RENDERIZAÇÃO DO MAPA
# =========================================================================
if os.path.exists(ARQUIVO_ROTA_DISCO):
    df_rota = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
    df_rota.columns = [str(c).strip().upper() for c in df_rota.columns]
    
    # Identificar Colunas
    col_sup = next((c for c in df_rota.columns if 'SUPERVISOR' in c), None)
    col_x = next((c for c in df_rota.columns if 'COORDENADA X' in c or 'LONG' in c), None)
    col_y = next((c for c in df_rota.columns if 'COORDENADA Y' in c or 'LATI' in c), None)
    col_tec = next((c for c in df_rota.columns if 'RECURSO' in c or 'NOME' in c), df_rota.columns[0])
    col_cidade = next((c for c in df_rota.columns if 'CIDADE' in c), None)
    
    if col_sup and col_x and col_y:
        
        # 1. FILTRO: APENAS CIDADES DO ABC (IGNORA SÃO PAULO)
        if col_cidade:
            df_rota = df_rota[df_rota[col_cidade].notna()]
            cond_cidade_base = df_rota[col_cidade].astype(str).str.upper().str.contains('DIADEMA|SANTO ANDRE|BERNARDO|SBC', regex=True)
            df_rota = df_rota[cond_cidade_base]

        # 2. FILTRO: TIPO DE ATIVIDADE (IGNORA RETORNOS)
        col_tipo_os = next((c for c in df_rota.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c or 'ATIVIDADE3' in c), None)
        if not col_tipo_os: col_tipo_os = next((c for c in df_rota.columns if 'TIPO O.S' in c or 'ATIVIDADE' in c), None)
        if col_tipo_os:
            df_rota = df_rota[df_rota[col_tipo_os].notna()]
            df_rota = df_rota[~df_rota[col_tipo_os].astype(str).str.upper().str.contains('RETORNO CREDENCIADA', na=False)]

        # 3. FILTRO PRINCIPAL: APENAS STATUS "EM ABERTO"
        col_status_ativ = next((c for c in df_rota.columns if 'STATUS DA ATIVIDADE' in c), None)
        col_status = next((c for c in df_rota.columns if 'STATUS CONTRATO' in c or 'STATUS_TV' in c), None)
        if not col_status: col_status = col_status_ativ
        if not col_status: col_status = next((c for c in df_rota.columns if 'STATUS' in c), None)
        
        if col_status:
            df_rota['STATUS_PADRAO'] = df_rota[col_status].apply(padronizar_status)
            df_rota = df_rota[df_rota['STATUS_PADRAO'] == 'Em aberto']

        # 4. LIMPAR SUPERVISORES E COORDENADAS
        df_rota['SUPERVISOR_CLEAN'] = df_rota.apply(lambda row: class_sup_mapa(row, col_sup), axis=1)
        df_mapa = df_rota[df_rota['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()
        
        df_mapa['LAT'] = pd.to_numeric(df_mapa[col_y].astype(str).str.replace(',', '.'), errors='coerce')
        df_mapa['LON'] = pd.to_numeric(df_mapa[col_x].astype(str).str.replace(',', '.'), errors='coerce')
        df_mapa = df_mapa.dropna(subset=['LAT', 'LON'])
        
        # Pegar apenas o primeiro nome do técnico
        df_mapa['NOME_TECNICO'] = df_mapa[col_tec].fillna('Desconhecido').astype(str).apply(lambda x: x.split()[0].upper())
        df_mapa['COLOR_RGB'] = df_mapa['SUPERVISOR_CLEAN'].apply(cor_sup_rgb)
        
        # 5. FILTRAR PELA OPÇÃO DO MENU LATERAL
        if "EDSON MARCO" in visao_selecionada:
            df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "EDSON MARCO"]
        elif "MAICON" in visao_selecionada:
            df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "MAICON"]
        elif "NELSON" in visao_selecionada:
            df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "NELSON"]
            
        # 6. RENDERIZAR O MAPA SE HOUVER DADOS
        if not df_mapa.empty:
            # Construir Legenda Visual Inteligente
            base_style = "display: flex; justify-content: center; gap: 30px; margin-bottom: 5px; font-size: 24px; font-weight: 900; color: #000000 !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);"
            
            if "GERAL" in visao_selecionada:
                legenda_html = f'''
                <div style="{base_style}">
                    <div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #800080; border-radius: 50%; border: 1px solid #000;"></span> EDSON MARCO</div>
                    <div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #FF1493; border-radius: 50%; border: 1px solid #000;"></span> MAICON</div>
                    <div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #008000; border-radius: 50%; border: 1px solid #000;"></span> NELSON</div>
                </div>
                '''
            elif "EDSON" in visao_selecionada:
                legenda_html = f'<div style="{base_style}"><div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #800080; border-radius: 50%; border: 1px solid #000;"></span> EDSON MARCO</div></div>'
            elif "MAICON" in visao_selecionada:
                legenda_html = f'<div style="{base_style}"><div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #FF1493; border-radius: 50%; border: 1px solid #000;"></span> MAICON</div></div>'
            else:
                legenda_html = f'<div style="{base_style}"><div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #008000; border-radius: 50%; border: 1px solid #000;"></span> NELSON</div></div>'

            st.markdown(legenda_html, unsafe_allow_html=True)
            
            # Construir Camadas do PyDeck
            scatter_layer = pdk.Layer(
                'ScatterplotLayer',
                data=df_mapa,
                get_position='[LON, LAT]',
                get_color='COLOR_RGB',
                get_radius=150,
                pickable=True,
                opacity=0.8
            )
            
            text_layer = pdk.Layer(
                "TextLayer",
                data=df_mapa,
                get_position="[LON, LAT]",
                get_text="NOME_TECNICO",
                get_size=16,
                get_color=[0, 0, 0],
                get_alignment_baseline="'bottom'",
                get_offset="[0, -15]"
            )
            
            # Lógica do Zoom Inteligente
            lat_min, lat_max = df_mapa['LAT'].min(), df_mapa['LAT'].max()
            lon_min, lon_max = df_mapa['LON'].min(), df_mapa['LON'].max()
            max_diff = max(lat_max - lat_min, lon_max - lon_min)
            
            if max_diff <= 0.05: zoom_dinamico = 13.5
            elif max_diff <= 0.1: zoom_dinamico = 12.5
            elif max_diff <= 0.2: zoom_dinamico = 11.5
            else: zoom_dinamico = 10.5
                
            view_state = pdk.ViewState(
                latitude=df_mapa['LAT'].mean(), 
                longitude=df_mapa['LON'].mean(), 
                zoom=zoom_dinamico, 
                pitch=0
            )
            
            r = pdk.Deck(
                layers=[scatter_layer, text_layer], 
                initial_view_state=view_state, 
                map_provider='carto',
                map_style='light',
                tooltip={"text": "{NOME_TECNICO}\nSupervisor: {SUPERVISOR_CLEAN}"}
            )
            
            st.pydeck_chart(r, use_container_width=True)
            
        else:
            st.warning("⚠️ Nenhum contrato pendente com coordenada válida encontrada para este supervisor nas cidades do ABC.")
        
    else:
        st.error("Colunas essenciais (Coordenada X, Coordenada Y ou Supervisor) não foram encontradas no arquivo.")
else:
    st.error("Ficheiro 'rota_sincronizada.csv' não encontrado. Realize a sincronização primeiro na aba Home.")
