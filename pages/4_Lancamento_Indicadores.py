import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Lançamento de Indicadores", layout="centered")

# Busca a lista de supervisores atualizada
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"
ARQUIVO_INDICADORES = "indicadores_data.csv"

supervisores_lista = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO"] # Fallback
try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        supervisores_lista = sorted([str(s).strip().upper() for s in df_equipe["SUPERVISOR"].dropna().unique().tolist() if str(s).strip() != ""])
except:
    pass

# Cria ou lê o arquivo de dados
if os.path.exists(ARQUIVO_INDICADORES):
    df_ind = pd.read_csv(ARQUIVO_INDICADORES)
else:
    df_ind = pd.DataFrame(columns=["INDICADOR", "BASE", "SUPERVISOR", "VALOR"])

st.markdown('<h1 style="color: #008080; text-align: center;">📥 Lançamento Diário de Indicadores</h1>', unsafe_allow_html=True)
st.write("Insira a pontuação da equipe. Os dados aparecerão na TV do Painel Rotativo.")

with st.form("form_ind"):
    indicador = st.selectbox("Selecione o Indicador:", ["NR35", "Certidão de Atendimento", "Band Steering"])
    base = st.selectbox("Base:", ["ABC", "SP"])
    supervisor = st.selectbox("Supervisor:", supervisores_lista)
    valor = st.number_input("Quantidade de Contratos/Registros:", min_value=0, step=1)
    
    submit = st.form_submit_button("💾 Salvar Registro no Painel")
    
    if submit:
        # Se já existir um lançamento para este indicador/supervisor, ele atualiza o número
        mask = (df_ind["INDICADOR"] == indicador) & (df_ind["BASE"] == base) & (df_ind["SUPERVISOR"] == supervisor)
        if mask.any():
            df_ind.loc[mask, "VALOR"] = valor
        else:
            novo_dado = pd.DataFrame([{"INDICADOR": indicador, "BASE": base, "SUPERVISOR": supervisor, "VALOR": valor}])
            df_ind = pd.concat([df_ind, novo_dado], ignore_index=True)
        
        df_ind.to_csv(ARQUIVO_INDICADORES, index=False)
        st.success(f"✅ Registro de {indicador} para {supervisor} ({base}) salvo com sucesso na TV!")

st.divider()

c1, c2 = st.columns([3, 1])
c1.markdown("### 📋 Registros Lançados Hoje")

# Botão para zerar os indicadores no dia seguinte
if c2.button("🗑️ Limpar Todos os Dados"):
    df_ind = pd.DataFrame(columns=["INDICADOR", "BASE", "SUPERVISOR", "VALOR"])
    df_ind.to_csv(ARQUIVO_INDICADORES, index=False)
    st.rerun()

st.dataframe(df_ind, use_container_width=True)
