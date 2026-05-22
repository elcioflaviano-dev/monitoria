import streamlit as st
import pandas as pd
import requests
import io

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado e ajustado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# === FUNÇÃO DE CARGA OPERACIONAL DO GOOGLE SHEETS COM VARREDURA INTEGRA ===
def carregar_dados_automatico():
    if 'dados_rota' in st.session_state:
        return st.session_state['dados_rota']
        
    try:
        # Puxa a URL configurada no Secrets da nuvem com fallback para o seu link direto
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = "https://docs.google.com/spreadsheets/d/" + id_planilha + "/export?format=csv"
            
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += "&gid=" + gid
            else:
                csv_url += "&gid=208394608"
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        
        if resposta.status_code != 200:
            return None
            
        conteudo_bruto = resposta.text
        if '<html' in conteudo_bruto.lower() or '<!doctype' in conteudo_bruto.lower():
            st.error("🔒 Erro de Permissão: A planilha está PRIVADA. Altere o compartilhamento no Google Sheets para 'Qualquer pessoa com o link'.")
            return None

        # Varredura inteligente para ignorar linhas de títulos decorativas ou mescladas no topo
        linhas_puras = conteudo_bruto.splitlines()
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        
        for i, linha_texto in enumerate(linhas_puras[:50]):
            linha_upper = linha_texto.upper()
            if 'SUPERVISOR' in linha_upper or 'STATUS' in linha_upper or 'JANELA' in linha_upper or 'CONTRATO' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        if df_sheets is None or df_sheets.empty:
            return None

        # Normalização rigorosa de cabeçalhos eliminando espaços ocultos
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        # Mapeamento dinâmico para garantir compatibilidade com as colunas do seu código original
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'Recurso'
            
        df_final = df_sheets.rename(columns=colunas_mapeadas)
        st.session_state['dados_rota'] = df_final
        return df_final
    except:
        return None

# Executa a carga inteligente
df_planilha = carregar_dados_automatico()

if df_planilha is not None:
    df = df_planilha.copy()
    
    # --- FILTRO DA JANELA GLOBAL (BARRA LATERAL) ---
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()
        janela_sel = "N/A"

    # --- SEPARAÇÃO LÓGICA DOS SUPERVISORES ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns:
        for idx, Server_linha in df_tela.iterrows():
            nome_super = str(Server_linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(Server_linha)
            else:
                df_abc_lista.append(Server_linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

    # --- CORPO VISUAL (COLUNAS LADO A LADO) ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- COLUNA ESQUERDA: ABC ---
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty and col_supervisor in df_abc.columns:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'PENDENTE']) if 'Status da Atividade' in df_super.columns else 0
                em_rota = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'EM ROTA']) if 'Status da Atividade' in df_super.columns else 0
                iniciados = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'INICIADO']) if 'Status da Atividade' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")

    # --- COLUNA DIREITA: SP ---
    with col_coluna_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        
        if not df_sp.empty and col_supervisor in df_sp.columns:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'PENDENTE']) if 'Status da Atividade' in df_super.columns else 0
                em_rota = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'EM ROTA']) if 'Status da Atividade' in df_super.columns else 0
                iniciados = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'INICIADO']) if 'Status da Atividade' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")

    # === AUTOMAÇÃO MODO TV (TROCA APÓS 30 SEGUNDOS) ===
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#2-tec1-pendentes";
        }, 30000);
        </script>
    """, height=0)

else:
    st.error("⚠️ Não foi possível obter dados estáveis da planilha online ou os cabeçalhos não estão alinhados.")
