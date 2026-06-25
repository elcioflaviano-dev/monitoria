# -------------------------------------------------------------------------
    # TELA 6: PAINEL DO CONSULTIVO DIÁRIO 🚀
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 6:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PERFORMANCE CONSULTIVO DIÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_mudo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
                df_cons.columns = [str(c).strip().upper().replace(' ', '_') for c in df_cons.columns]

                # 1. Limpeza de colunas obrigatórias
                df_cons['BASE'] = df_cons['BASE'].fillna('N/D').apply(limpar_texto)
                df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
                
                # 2. Força a coluna DATA para string e remove espaços
                df_cons['DATA'] = df_cons['DATA'].astype(str).str.strip()
                
                # 3. Tratamento numérico da quantidade
                col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
                df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int) if col_qtd else 0

                # Data de hoje como texto no formato exato do CSV (DD/MM/AAAA)
                hoje_str = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')
                
                # Filtros
                df_cards = df_cons[df_cons['SUPERVISOR'] != 'DESCARTADO'].copy()
                df_hoje = df_cons[df_cons['DATA'] == hoje_str].copy()
                
                # Cálculo de dias úteis
                hoje = datetime.utcnow() - timedelta(hours=3)
                _, num_dias = calendar.monthrange(hoje.year, hoje.month)
                dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
                if dias_restantes == 0: dias_restantes = 1

                # Renderização
                col_abc, col_sp = st.columns(2)
                
                def exibir_cards(base, col, sups):
                    with col:
                        # Card de dias restantes no topo da coluna
                        st.markdown(f'<div style="text-align: center; margin-bottom: 20px; font-weight:bold; font-size:20px;">Dias úteis restantes: {dias_restantes}</div>', unsafe_allow_html=True)
                        for sup in sups:
                            # Filtro robusto pelo nome
                            mask_mes = df_cards['SUPERVISOR'].str.contains(sup.split()[0], na=False) & (df_cards['BASE'] == base)
                            mask_hoje = df_hoje['SUPERVISOR'].str.contains(sup.split()[0], na=False) & (df_hoje['BASE'] == base)
                            
                            qtd_mes = df_cards[mask_mes]['QTD_PRODUTOS_CALC'].sum()
                            qtd_hoje = df_hoje[mask_hoje]['QTD_PRODUTOS_CALC'].sum()
                            
                            meta_dia = round(max(0, 350 - qtd_mes) / dias_restantes, 1)
                            falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)

                            st.markdown(f'''
                            <div class="sup-card">
                                <div class="sup-header">
                                    <div class="sup-name" style="font-size: 26px;">📋 {obter_nome_visual(sup)}</div>
                                    <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32;">Acumulado: {qtd_mes}</div>
                                </div>
                                <div class="faltas-grid">
                                    <div class="falta-box" style="background-color: #e8f5e9;"><div class="falta-label" style="color: #2e7d32;">📦 HOJE</div><div class="falta-value" style="color: #1b5e20;">{qtd_hoje}</div></div>
                                    <div class="falta-box" style="background-color: #ffebee;"><div class="falta-label" style="color: #c62828;">📉 FALTAM</div><div class="falta-value" style="color: #b30000;">{falta_hoje}</div></div>
                                    <div class="falta-box" style="background-color: #fff8e1;"><div class="falta-label" style="color: #b78103;">🎯 META DIA</div><div class="falta-value" style="color: #b78103;">{meta_dia}</div></div>
                                </div>
                            </div>''', unsafe_allow_html=True)

                exibir_cards('ABC', col_abc, SUPS_ABC)
                exibir_cards('SP', col_sp, SUPS_SP)

            except Exception as e:
                st.error(f"Erro na exibição: {e}")
        else:
            st.warning("Arquivo de dados não encontrado.")
