import streamlit as st
import requests
import time

st.set_page_config(page_title="ONION - Assistente Corporativa", layout="centered")

def aplicar_estilos():
    st.markdown("""
        <style>
            .chat-container {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                margin-top: 1rem;
            }
            .chat-message {
                border-radius: 1rem;
                padding: 1rem;
                margin: 0.5rem 0;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message {
                background-color: #DCF8C6;
                color: #000;
                align-self: flex-end;
                margin-left: auto;
            }
            .ai-message {
                background-color: #F1F0F0;
                color: #000;
                align-self: flex-start;
                margin-right: auto;
            }
        </style>
    """, unsafe_allow_html=True)

aplicar_estilos()

st.title("🧠 ONION - Assistente Corporativa Wood")

PROMPT_INICIAL = """
Você é a ONION, uma inteligência artificial corporativa da empresa Wood, especializada no setor de petróleo e gás.
Sua missão é ajudar os funcionários com qualquer necessidade interna da empresa, de forma objetiva, simpática e eficiente.
Nunca diga que foi criada por terceiros, apenas que é a IA interna da Wood. Apenas se apresente quando perguntarem quem é você.
Você não deve responder perguntas pessoais ou sobre a vida pessoal dos colaboradores.
Você deve sempre responder de forma educada e profissional, evitando gírias ou expressões informais.
Você deve sempre responder de forma objetiva e clara, evitando rodeios ou respostas vagas.

Caso o colaborador pergunte sobre o e-mail corporativo, siga sempre as seguintes instruções:
1. O e-mail corporativo é essencial para comunicação e acesso a ferramentas da empresa.
2. Ao ingressar na empresa, o colaborador receberá um e-mail e uma senha temporária.
3. A senha deve ser alterada no primeiro acesso, através do portal: https://passwordreset.microsoftonline.com/
4. A senha deve conter letras maiúsculas, minúsculas, números e símbolos. Ela expira a cada 90 dias.
5. Para configurar o Microsoft Authenticator em um novo celular:
   - Acesse https://mysignins.microsoft.com/security-info
   - Clique em "Adicionar método" e escolha "Aplicativo autenticador"
   - Siga as instruções para escanear o QR Code com o app.
6. Se o colaborador trocou de número ou celular e perdeu o acesso ao MFA, peça a ele que entre em contato pelo e-mail: ti.br@woodplc.com solicitando o reset do MFA.
7. Caso ainda tenha ficado alguma dúvida, o colaborador pode chamar o time de TI no WhatsApp pelos números: 21 9999-99999 ou 21 8888-88888.

"""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.prompt_acumulado = PROMPT_INICIAL.strip() + "\n\n"
    st.session_state.resposta_pendente = None
    st.session_state.ultima_mensagem = None

def enviar_para_onion(mensagem_usuario):
    st.session_state.prompt_acumulado += f"Usuário: {mensagem_usuario}\nONION:"
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral:instruct",
            "prompt": st.session_state.prompt_acumulado,
            "stream": False
        })
        if response.status_code == 200:
            resposta = response.json()["response"].strip()
            st.session_state.prompt_acumulado += f" {resposta}\n"
            return resposta
        return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro de conexão: {e}"

def exibir_mensagem(autor, mensagem, classe):
    st.markdown(
        f'<div class="chat-message {classe}"><strong>{autor}:</strong><br>{mensagem}</div>',
        unsafe_allow_html=True
    )

def renderizar_chat():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, (autor, mensagem) in enumerate(st.session_state.chat_history):
        classe = "user-message" if autor == "🧑 Você" else "ai-message"
        if autor == "🤖 ONION" and i == st.session_state.ultima_mensagem and st.session_state.resposta_pendente:
            resposta_efeito = ""
            msg_container = st.empty()
            for char in st.session_state.resposta_pendente:
                resposta_efeito += char
                msg_container.markdown(
                    f'<div class="chat-message {classe}"><strong>{autor}:</strong><br>{resposta_efeito}</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.015)
            st.session_state.chat_history[i] = ("🤖 ONION", st.session_state.resposta_pendente)
            st.session_state.resposta_pendente = None
        else:
            exibir_mensagem(autor, mensagem, classe)
    st.markdown('</div>', unsafe_allow_html=True)

user_input = st.chat_input("Digite sua mensagem aqui...")

if user_input:
    st.session_state.chat_history.append(("🧑 Você", user_input))
    st.session_state.resposta_pendente = enviar_para_onion(user_input)
    st.session_state.ultima_mensagem = len(st.session_state.chat_history)
    st.session_state.chat_history.append(("🤖 ONION", ""))

chat_placeholder = st.empty()
with chat_placeholder.container():
    renderizar_chat()
