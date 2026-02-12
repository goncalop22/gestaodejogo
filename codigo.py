import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- Configuração da Página ---
st.set_page_config(
    page_title="Relatório de jogo PRO",
    page_icon="⚽",
    layout="wide"
)

# --- Gestão de Estado (Session State) ---
# Isto garante que os dados não se perdem quando clicas num botão
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
    
    # Calcular minuto do jogo
    minuto = 0
    if st.session_state['inicio_jogo']:
        delta = agora - st.session_state['inicio_jogo']
        minuto = int(delta.total_seconds() // 60) + 1
    
    # Adicionar ao registo
    novo_evento = {
        "Minuto": minuto,
        "Equipa": equipa,
        "Evento": tipo_evento,
        "Hora Real": agora.strftime("%H:%M:%S")
    }
    st.session_state['eventos'].append(novo_evento)
    
    # Feedback visual rápido
    st.toast(f"✅ {tipo_evento} registado ({equipa})!")

# --- Interface Principal ---
st.title("⚽ Relatório de jogo: Painel de Jogo")

# Sidebar para Configurações
with st.sidebar:
    st.header("Configurações")
    equipa_casa = st.text_input("Minha Equipa", "Minha Equipa")
    equipa_fora = st.text_input("Adversário", "Adversário")
    
    st.divider()
    
    # Controlo do Cronómetro
    if st.session_state['inicio_jogo'] is None:
        if st.button("⏱️ Iniciar Jogo", type="primary"):
            iniciar_jogo()
            st.rerun()
    else:
        tempo_decorrido = datetime.now() - st.session_state['inicio_jogo']
        minutos_jogados = int(tempo_decorrido.total_seconds() // 60) + 1
        st.metric(label="Tempo de Jogo", value=f"{minutos_jogados}' Min")
        
        if st.button("⏹️ Terminar/Resetar"):
            resetar_dados()
            st.rerun()

# --- Área de Ação (Botões Grandes) ---
# Usamos Tabs para separar ações da Minha Equipa vs Adversário (para não enganar no clique)
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

# --- Processamento de Dados e Estatísticas ---
with tab3:
    if len(st.session_state['eventos']) > 0:
        # Criar DataFrame
        df = pd.DataFrame(st.session_state['eventos'])
        
        # Dashboard Rápido
        st.subheader("Resumo do Jogo")
        
        # Contagem de Eventos por Equipa
        stats = df.pivot_table(index='Evento', columns='Equipa', aggfunc='size', fill_value=0)
        st.dataframe(stats, use_container_width=True)
        
        # Gráfico de Barras
        st.bar_chart(df['Evento'].value_counts())
        
        # Histórico Completo (Log)
        st.subheader("Log de Eventos")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True) # Mostra o último evento primeiro
        
        # Botão de Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatório (CSV)",
            data=csv,
            file_name=f'scout_jogo_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.info("Ainda não há eventos registados. O jogo vai começar!")
