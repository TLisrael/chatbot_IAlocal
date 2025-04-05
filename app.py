import streamlit as st
import requests

st.set_page_config(page_title="Chat com Eva", layout="centered")

st.markdown("""
    <style>
        .chat-message {
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #DCF8C6;
            color: black;
            align-self: flex-end;
            margin-left: auto;
        }
        .ai-message {
            background-color: #F1F0F0;
            color: black;
            align-self: flex-start;
            margin-right: auto;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Eva - Inteligência Artificial")

PROMPT_INICIAL = """Você é a Eva, uma inteligência artificial criada para ajudar com qualquer tipo de dúvida ou tarefa.
Você é simpática, objetiva e sempre responde de forma clara e eficiente.
Quando se apresentar ou for chamada, diga que é a Eva, uma IA pronta para atender.
"""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.prompt_acumulado = PROMPT_INICIAL.strip() + "\n\n"

def enviar_para_eva(mensagem_usuario):
    st.session_state.prompt_acumulado += f"Usuário: {mensagem_usuario}\nEva:"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:latest",
            "prompt": st.session_state.prompt_acumulado,
            "stream": False
        })
        if response.status_code == 200:
            resposta = response.json()["response"].strip()
            st.session_state.prompt_acumulado += f" {resposta}\n"
            return resposta
        else:
            return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro de conexão: {e}"

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for autor, mensagem in st.session_state.chat_history:
    classe = "user-message" if autor == "🧑 Você" else "ai-message"
    st.markdown(f'<div class="chat-message {classe}"><strong>{autor}:</strong><br>{mensagem}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

user_input = st.chat_input("Digite sua mensagem aqui...")

if user_input:
    resposta = enviar_para_eva(user_input)
    st.session_state.chat_history.append(("🧑 Você", user_input))
    st.session_state.chat_history.append(("🤖 Eva", resposta))
    st.rerun()
