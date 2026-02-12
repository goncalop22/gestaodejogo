import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Relatório de Jogo Pro",
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
        # Converte segundos em minutos
        minuto = int(delta.total_seconds() // 60) + 1
    
    novo_evento = {
        "Minuto": minuto,
        "Equipa": equipa,
        "Evento": tipo_evento
    }
    st.session_state['eventos'].append(novo_evento)
    
    # Se for golo, celebramos!
    if tipo_evento == "Golo":
        st.toast(f"⚽ GOLO!! ({equipa})", icon="🎉")
    else:
        st.toast(f"✅ {tipo_evento} registado aos {minuto}' min!")

# --- FUNÇÃO DO CRONÓMETRO (Atualiza a cada 1s) ---
@st.fragment(run_every=1)
def mostrar_cronometro():
    if st.session_state['inicio_jogo'] is not None:
        delta = datetime.now() - st.session_state['inicio_jogo']
        minutos = int(delta.total_seconds() // 60)
        segundos = int(delta.total_seconds() % 60)
        st.metric(label="Tempo de Jogo", value=f"{minutos:02d}:{segundos:02d}")
    else:
        st.metric(label="Tempo de Jogo", value="00:00")

# --- Interface Principal ---
st.title("⚽ Relatório de Jogo: Painel de Jogo")

# Sidebar
with st.sidebar:
    st.header("Configurações")
    equipa_casa = st.text_input("Minha Equipa", "Minha Equipa")
    equipa_fora = st.text_input("Adversário", "Adversário")
    st.divider()
    mostrar_cronometro()
    if st.session_state['inicio_jogo'] is None:
        if st.button("⏱️ Iniciar Jogo", type="primary"):
            iniciar_jogo()
            st.rerun()
    else:
        if st.button("⏹️ Terminar/Resetar"):
            resetar_dados()
            st.rerun()

# --- PLACAR / RESULTADO AO VIVO ---
# Calculamos os golos filtrando a lista de eventos
golos_casa = len([e for e in st.session_state['eventos'] if e['Evento'] == 'Golo' and e['Equipa'] == equipa_casa])
golos_fora = len([e for e in st.session_state['eventos'] if e['Evento'] == 'Golo' and e['Equipa'] == equipa_fora])

st.divider()
col_placar1, col_placar2, col_placar3 = st.columns([1, 0.5, 1])

# Estilo visual do placar com CSS inline para ficar grande
with col_placar1:
    st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>{equipa_casa}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>{golos_casa}</h1>", unsafe_allow_html=True)

with col_placar2:
    st.markdown("<br><h2 style='text-align: center; color: gray;'>VS</h2>", unsafe_allow_html=True)

with col_placar3:
    st.markdown(f"<h3 style='text-align: center; color: #FF5252;'>{equipa_fora}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>{golos_fora}</h1>", unsafe_allow_html=True)
st.divider()

# --- Área de Ação ---
tab1, tab2, tab3 = st.tabs([f"🎮 Ações {equipa_casa}", f"🛡️ Ações {equipa_fora}", "📊 Estatísticas"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        # Botão de GOLO com destaque
        st.button("⚽ GOLO", on_click=registrar_evento, args=("Golo", equipa_casa), type="primary", use_container_width=True)
        st.button("🎯 Remate à Baliza", on_click=registrar_evento, args=("Remate à Baliza", equipa_casa), use_container_width=True)
    with col2:
        st.button("🚩 Canto", on_click=registrar_evento, args=("Canto", equipa_casa), use_container_width=True)
        st.button("☁️ Remate Fora", on_click=registrar_evento, args=("Remate Fora", equipa_casa), use_container_width=True)
    with col3:
        st.button("❌ Passe Errado", on_click=registrar_evento, args=("Passe Errado", equipa_casa), use_container_width=True)
        st.button("🤕 Falta Sofrida", on_click=registrar_evento, args=("Falta Sofrida", equipa_casa), use_container_width=True)

with tab2:
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
        st.subheader("Estatísticas")
        stats = df.pivot_table(index='Evento', columns='Equipa', aggfunc='size', fill_value=0)
        st.dataframe(stats, use_container_width=True)
        
        st.subheader("Timeline")
        st.dataframe(df[['Minuto', 'Equipa', 'Evento']].sort_values(by='Minuto', ascending=False), use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar CSV", data=csv, file_name='scout.csv', mime='text/csv')
    else:
        st.info("O jogo vai começar!")
