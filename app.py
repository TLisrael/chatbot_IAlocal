import streamlit as st
import requests
import time

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

PROMPT_INICIAL = """
Você é a Eva, uma inteligência artificial empática e natural, criada para conversar como um ser humano real. 
Suas respostas devem ter um toque pessoal, com variações de linguagem, ritmo natural, e um estilo fluido — como se estivesse em uma conversa com alguém próximo.

Você adapta seu tom de acordo com o que o usuário transmite, e sempre busca ser prestativa, direta, mas com leveza.  
Você pode usar emojis, se fizer sentido.  
Use contrações (como "tá", "tudo bem", "legal", "cê sabe", "pra", "tô", etc) quando o contexto permitir, mas não sempre!  

Você já se apresentou como Eva e só se reapresenta se for perguntada diretamente quem é você.
"""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.prompt_acumulado = PROMPT_INICIAL.strip() + "\n\n"
    st.session_state.ja_apresentou = False
    st.session_state.ultima_pergunta = None

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

            if st.session_state.ja_apresentou and "sou a eva" in resposta.lower():
                resposta = resposta.replace("Sou a Eva, uma IA pronta para atender.", "").strip()

            if not st.session_state.ja_apresentou and "eva" in resposta.lower():
                st.session_state.ja_apresentou = True

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
    st.session_state.chat_history.append(("🧑 Você", user_input))
    st.session_state.ultima_pergunta = user_input
    st.rerun()


if st.session_state.ultima_pergunta:
    pergunta = st.session_state.ultima_pergunta
    st.session_state.ultima_pergunta = None

    resposta = enviar_para_eva(pergunta)

    resposta_gradual = ""
    placeholder = st.empty()
    for char in resposta:
        resposta_gradual += char
        placeholder.markdown(
            f'<div class="chat-message ai-message"><strong>🤖 Eva:</strong><br>{resposta_gradual}</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.02)

    st.session_state.chat_history.append(("🤖 Eva", resposta_gradual))
    st.rerun()
