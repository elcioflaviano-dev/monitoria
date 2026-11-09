st.markdown("""<style>
    /* Ajuste seguro para manter o conteúdo visível na TV */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 50px !important; max-width: 98% !important; }
    
    /* Removemos o overflow: hidden do html/body para evitar que a tela fique em branco */
    ::-webkit-scrollbar { display: none !important; }

    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 0px 20px; border-radius: 0 0 10px 10px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 75px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 16px; font-weight: bold; border: 2px solid #fff; padding: 6px 12px; border-radius: 5px; text-decoration: none; }
    
    .st-key-btn_anterior { position: fixed !important; bottom: 65px !important; left: 20px !important; z-index: 999999 !important; width: auto !important; }
    .st-key-btn_proxima, .st-key-btn_atualizar_estatico { position: fixed !important; bottom: 65px !important; right: 20px !important; z-index: 999999 !important; width: auto !important; }
    
    .st-key-btn_anterior button, .st-key-btn_proxima button, .st-key-btn_atualizar_estatico button { 
        background-color: #003366 !important; color: #ffffff !important; border: 2px solid #ffffff !important; border-radius: 30px !important; padding: 6px 15px !important; font-size: 15px !important; font-weight: bold !important; opacity: 0.03 !important; transition: all 0.4s ease-in-out !important; 
    }
    .st-key-btn_anterior button:hover, .st-key-btn_proxima button:hover, .st-key-btn_atualizar_estatico button:hover { 
        opacity: 1.0 !important; background-color: #ff9800 !important; border-color: #ffffff !important; transform: scale(1.05) !important; 
    }

    [data-testid="stDeckGlJsonChart"] { height: 72vh !important; min-height: 550px !important; border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15); }

    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 8px 10px; text-align: center; border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px !important; font-weight: 900; color: #2e7d32; text-transform: uppercase; margin-bottom: 2px; }
    .num-base { font-size: 80px !important; font-weight: 900; color: #111; line-height: 1; }
    
    .sup-card { background: #ffffff; border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .sup-name { font-size: 30px !important; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { background: #ffebee; color: #c62828; padding: 6px 15px; border-radius: 8px; font-size: 20px !important; font-weight: 900; border: 2px solid #ffcdd2; }
    .faltas-grid { display: flex; justify-content: space-between; gap: 12px; }
    .falta-box { background-color: #ffebee; border: 2px solid #ffcdd2; border-radius: 8px; padding: 10px 5px; text-align: center; margin-bottom: 0px; flex: 1; }
    .falta-label { font-size: 15px !important; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 55px !important; font-weight: 900; color: #b30000; line-height: 1; }
    
    .box-contagem { background: #ffffff; border: 2px solid #e0e0e0; border-left: 12px solid #cc6600; padding: 15px; border-radius: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; position: relative; z-index: 1; transition: 0.3s; }
    .box-nome { font-size: 35px !important; font-weight: 900; color: #003366; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }
    .destaque-ativo { transform: scale(1.05) !important; box-shadow: 0px 15px 30px rgba(204, 102, 0, 0.4) !important; border-left: 18px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 220px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 50px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 12px 15px; border-left: 6px solid #008080; border-radius: 6px; margin-bottom: 10px; font-weight: bold; font-size: 24px !important; color: #333; box-shadow: 1px 1px 4px rgba(0,0,0,0.1); }

    .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; overflow: hidden; height: 50px; background-color: #002244; box-sizing: border-box; z-index: 99999; border-top: 3px solid #ff8800; display: flex; align-items: center; }
    .ticker { display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 45s linear infinite; }
    .ticker__item { display: inline-block; padding: 0 15px; font-size: 20px; color: #ffffff; font-weight: 900; text-transform: uppercase; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>""", unsafe_allow_html=True)
