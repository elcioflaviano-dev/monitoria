import streamlit.components.v1 as components

# Função para disparar som de alerta
def tocar_alerta():
    # Este link é um exemplo de som. Se tiver um arquivo .mp3 local, podemos usar também.
    js_code = """
    <script>
        var audio = new Audio('https://www.soundjay.com/buttons/beep-07.wav');
        audio.play();
    </script>
    """
    components.html(js_code, height=0)

# Função para Voz (TTS) - Caso queira que ele "fale" algo
def falar_texto(texto):
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance('{texto}');
        msg.lang = 'pt-BR';
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)
