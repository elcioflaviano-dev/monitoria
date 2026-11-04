# 3. Tratamento de Metas e Histórico de O.S. (Blindado para o mês do CSV)
        meta_diaria_base = 454
        hoje_dt = datetime.utcnow() - timedelta(hours=3)
        
        meta_diaria_hoje = 0 if hoje_dt.weekday() == 6 else meta_diaria_base
        
        realizado_passado = 0
        meta_passada = 0
        qtd_dias_passados_uteis = 0
        
        primeiro_dia_mes = hoje_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        hoje_meia_noite = hoje_dt.replace(hour=0, minute=0, second=0, microsecond=0)

        if os.path.exists(ARQUIVO_HISTORICO_METAS):
            try:
                df_hist = pd.read_csv(ARQUIVO_HISTORICO_METAS, header=None, dtype=str, on_bad_lines='skip')
                if not df_hist.empty and df_hist.shape[1] >= 2:
                    # Converte a coluna de datas para objetos datetime para descobrir o mês ativo no CSV
                    datas_convertidas = []
                    for val_dt in df_hist[0].dropna():
                        txt_data = str(val_dt).strip().replace('"', '')
                        d_obj = pd.to_datetime(txt_data, format='%m/%d/%Y', errors='coerce')
                        if pd.isna(d_obj): d_obj = pd.to_datetime(txt_data, format='%d/%m/%Y', errors='coerce')
                        if pd.isna(d_obj): d_obj = pd.to_datetime(txt_data, format='%Y-%m-%d', errors='coerce')
                        if pd.notna(d_obj): datas_convertidas.append(d_obj)
                    
                    if datas_convertidas:
                        # Pega o mês e ano predominantes ou do último registro do CSV para alinhar a competência
                        ref_ano = datas_convertidas[-1].year
                        ref_mes = datas_convertidas[-1].month
                        primeiro_dia_mes = datetime(ref_ano, ref_mes, 1)
                        
                    for _, row in df_hist.iterrows():
                        txt_data = str(row[0]).strip().replace('"', '')
                        txt_valor = str(row[1]).strip().replace('"', '').replace(',', '.')
                        
                        d_obj = pd.to_datetime(txt_data, format='%m/%d/%Y', errors='coerce')
                        if pd.isna(d_obj): d_obj = pd.to_datetime(txt_data, format='%d/%m/%Y', errors='coerce')
                        if pd.isna(d_obj): d_obj = pd.to_datetime(txt_data, format='%Y-%m-%d', errors='coerce')
                            
                        # Soma todos os dias do mês presente no CSV que sejam estritamente anteriores a hoje (ou todos se o mês já passou)
                        if pd.notna(d_obj) and d_obj.year == primeiro_dia_mes.year and d_obj.month == primeiro_dia_mes.month:
                            if d_obj < hoje_meia_noite:
                                val_num = float(txt_valor) if txt_valor.replace('.', '', 1).isdigit() else 0
                                realizado_passado += int(val_num)
                                if d_obj.weekday() != 6:
                                    qtd_dias_passados_uteis += 1
                                    meta_passada += meta_diaria_base
            except Exception as e:
                print(f"Erro ao ler histórico de metas: {e}")

        deficit_acumulado = max(0, meta_passada - realizado_passado)
