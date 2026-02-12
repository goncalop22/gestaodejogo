import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="ScoutMaster Pro",
    page_icon="⚽",
    layout="wide"
)

# --- Gestão de Estado ---
if 'eventos' not in st.session_state:
    st.session_state['eventos'] = []
if 'inicio_jogo' not in st.session_state:
    st.session_state['inicio_jogo'] = None

# --- Funções Auxiliares ---
def iniciar_jogo():
    st.session_state['inicio_jogo'] = datetime.now()

def resetar_dados():
    st.session_state['eventos'] = []
    st.session_state['inicio_jogo'] = None

def registrar_evento(tipo_evento, equipa):
    agora = datetime.now()
    minuto = 0
    if st.session_state['inicio_jogo']:
        delta = agora - st.session_state['inicio_jogo']
        minuto = int(delta.total_seconds() // 60) + 1
    
    novo_evento = {
        "Minuto": minuto,
        "Equipa": equipa,
        "Evento": tipo_evento
    }
    st.session_state['eventos'].append(novo_evento)
    st.toast(f"✅ {tipo_evento} registado aos {minuto}' min!")

# --- FUNÇÃO ESPECIAL DO RELÓGIO (A MÁGICA ESTÁ AQUI) ---
# O 'run_every=1' faz esta função atualizar sozinha a cada 1 segundo
@st.fragment(run_every=1)
def mostrar_cronometro():
    if st.session_state['inicio_jogo'] is not None:
        delta = datetime.now() - st.session_state['inicio_jogo']
        # Formatar para MM:SS
        minutos = int(delta.total_seconds() // 60)
        segundos = int(delta.total_seconds() % 60)
        
        # Mostra o tempo formatado bonito (ex: 12:05)
        st.metric(
            label="Tempo de Jogo", 
            value=f"{minutos:02d}:{segundos:02d}",
            delta="A decorrer..."
        )
    else:
        st.metric(label="Tempo de Jogo", value="00:00")

# --- Interface Principal ---
st.title("⚽ ScoutMaster: Painel de Jogo")

# Sidebar
with st.sidebar:
    st.header("Configurações")
    equipa_casa = st.text_input("Minha Equipa", "Minha Equipa")
    equipa_fora = st.text_input("Adversário", "Adversário")
    st.divider()
    
    # Chama a função do relógio automático aqui
    mostrar_cronometro()
    
    if st.session_state['inicio_jogo'] is None:
        if st.button("⏱️ Iniciar Jogo", type="primary"):
            iniciar_jogo()
            st.rerun()
    else:
        if st.button("⏹️ Terminar/Resetar"):
            resetar_dados()
            st.rerun()

# --- Área de Ação ---
tab1, tab2, tab3 = st.tabs([f"🎮 {equipa_casa}", f"🛡️ {equipa_fora}", "📊 Dados"])

with tab1:
    st.subheader(f"Ações Ofensivas: {equipa_casa}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("⚽ GOLO", on_click=registrar_evento, args=("Golo", equipa_casa), type="primary", use_container_width=True)
        st.button("🎯 Remate à Baliza", on_click=registrar_evento, args=("Remate à Baliza", equipa_casa), use_container_width=True)
    with col2:
        st.button("🚩 Canto", on_click=registrar_evento, args=("Canto", equipa_casa), use_container_width=True)
        st.button("☁️ Remate Fora", on_click=registrar_evento, args=("Remate Fora", equipa_casa), use_container_width=True)
    with col3:
        st.button("❌ Passe Errado", on_click=registrar_evento, args=("Passe Errado", equipa_casa), use_container_width=True)
        st.button("🤕 Falta Sofrida", on_click=registrar_evento, args=("Falta Sofrida", equipa_casa), use_container_width=True)

with tab2:
    st.subheader(f"Registos do: {equipa_fora}")
    colA, colB = st.columns(2)
    with colA:
        st.button("Golo Sofrido", on_click=registrar_evento, args=("Golo", equipa_fora), type="primary", use_container_width=True)
        st.button("Remate Deles", on_click=registrar_evento, args=("Remate", equipa_fora), use_container_width=True)
    with colB:
        st.button("Falta Deles", on_click=registrar_evento, args=("Falta Cometida", equipa_fora), use_container_width=True)
        st.button("Canto Deles", on_click=registrar_evento, args=("Canto", equipa_fora), use_container_width=True)

with tab3:
    if len(st.session_state['eventos']) > 0:
        df = pd.DataFrame(st.session_state['eventos'])
        st.subheader("Resumo do Jogo")
        stats = df.pivot_table(index='Evento', columns='Equipa', aggfunc='size', fill_value=0)
        st.dataframe(stats, use_container_width=True)
        
        st.subheader("Cronologia")
        st.dataframe(df[['Minuto', 'Equipa', 'Evento']].sort_values(by='Minuto', ascending=False), use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar CSV", data=csv, file_name='scout.csv', mime='text/csv')
    else:
        st.info("O jogo ainda não começou.")
