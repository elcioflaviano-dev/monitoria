# CSS Ajustado para limitar a largura e alinhar
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:25px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:9999; display: flex; justify-content: space-between; align-items: center; }
    .btn-home { color:#fff; text-decoration:none; font-weight:bold; border:1px solid #fff; padding:5px 10px; border-radius:5px; font-size:16px; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 100px; color: #000; }
    /* Limita a largura do card para não esticar */
    .card-c { background:#eee; padding:8px; border-radius:4px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; max-width: 450px; }
    .conteudo { margin-top: 80px; }
    .grade-contratos { display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 10px; }
</style>""", unsafe_allow_html=True)

# ... (código de lógica de sessão e tempo igual ao anterior) ...

# Dentro do container (seção do supervisor):
with conteudo:
    st.markdown('<div class="conteudo">', unsafe_allow_html=True)
    if st.session_state.idx < len(SUPERVISORES):
        # ... (leitura e filtro) ...
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        
        # Grade fixada para não esticar
        st.markdown('<div class="grade-contratos">', unsafe_allow_html=True)
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
