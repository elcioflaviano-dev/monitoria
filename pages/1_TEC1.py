# === MÓDULO DE CARGA INTELIGENTE COM DIAGNÓSTICO SEGURO ===
def carregar_dados_sheets():
    try:
        url = st.secrets['public_gsheets_url']
        
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0]
            csv_url = 'https://docs.google.com/spreadsheets/d/' + id_planilha + '/export?format=csv'
            
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0]
                csv_url += '&gid=' + gid
            else:
                csv_url += '&gid=208394608'
        else:
            csv_url = url

        resposta = requests.get(csv_url, timeout=15)
        if resposta.status_code != 200:
            st.error('⚠️ Erro de conexão com o Google.')
            return None
            
        conteudo = resposta.text
        if '<html' in conteudo.lower() or '<!doctype' in conteudo.lower():
            st.error('🔒 Erro de Permissão: O link está privado no Google Sheets.')
            return None

        # Localiza a linha do cabeçalho
        linhas_puras = conteudo.splitlines()
        linha_do_cabecalho = 0
        
        for i, linha in enumerate(linhas_puras[:15]):
            linha_upper = linha.upper()
            if 'SUPERVISOR' in linha_upper or 'STATUS' in linha_upper or 'RECURSO' in linha_upper or 'JANELA' in linha_upper:
                linha_do_cabecalho = i
                break
        
        df_sheets = pd.read_csv(io.StringIO(conteudo), skiprows=linha_do_cabecalho, dtype=str)
        if df_sheets.empty:
            st.warning('⚠️ A tabela carregada está vazia após processar o cabeçalho.')
            return None
            
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'JANELA_SERVICO'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'CONTRATO'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'RECURSO'
            
        df = df_sheets.rename(columns=colunas_mapeadas)
        
        for col_obrigatoria in ['SUPERVISOR', 'JANELA_SERVICO', 'STATUS_ATIVIDADE']:
            if col_obrigatoria not in df.columns:
                df[col_obrigatoria] = 'N/A'
            else:
                df[col_obrigatoria] = df[col_obrigatoria].fillna('N/A')
                
        df['STATUS_ATIVIDADE'] = df['STATUS_ATIVIDADE'].apply(lambda x: str(x).strip().upper())
        return df
        
    except Exception as e:
        st.error('Erro de processamento interno detectado:')
        st.exception(e)  # <--- Renderiza o rastreio do erro de forma nativa e segura
        return None
