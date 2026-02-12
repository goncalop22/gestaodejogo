import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="ScoutMaster Pro", page_icon="⚽", layout="wide")

# --- Gestão de Estado ---
if 'eventos' not in st.session_state:
    st.session_state['eventos'] = []
if 'inicio_jogo' not in st.session_state:
    st.session_state['inicio_jogo'] = None
# Lista de jogadores padrão (podes mudar na sidebar)
if 'jogadores' not in st.session_state:
    st.session_state['jogadores'] = ["Tiago Duarte", "Gonçalo", "Rodrigo Silva", "Rafael Arraiano", "Rapha", "Casaca", "Kiko", "Mica", "Leandro", "Leonardo R.", "Martim", "Leonardo Alves", "Gabi", "Pinto", "Osmar", "Ju", "Bicho", "Liedson", "Godinho", "Rodrigo", "Fred"]

# --- Funções Auxiliares ---
def iniciar_jogo():
    st.session_state['inicio_jogo'] = datetime.now()

def resetar_dados():
    st.session_state['eventos'] = []
    st.session_state['inicio_jogo'] = None

def get_minuto_atual():
    if st.session_state['inicio_jogo']:
        delta = datetime.now() - st.session_state['inicio_jogo']
        return int(delta.total_seconds() // 60) + 1
    return 0

def registrar_evento(tipo_evento, equipa, jogador="Equipa"):
    minuto = get_minuto_atual()
    
    novo_evento = {
        "Minuto": minuto,
        "Equipa": equipa,
        "Jogador": jogador, # Nova coluna
        "Evento": tipo_evento
    }
    st.session_state['eventos'].append(novo_evento)
    
    # Feedback
    msg = f"✅ {tipo_evento}"
    if jogador != "Equipa":
        msg += f" de {jogador}"
    st.toast(msg, icon="⚽" if tipo_evento == "Golo" else "📝")

# --- MODAL DE SELEÇÃO DE JOGADOR ---
@st.dialog("Quem foi o craque? (ou o culpado 😅)")
def selecionar_jogador(tipo_evento, equipa):
    st.write(f"Registar **{tipo_evento}** para:")
    
    # Grelha de botões para os jogadores
    cols = st.columns(3)
    for i, jogador in enumerate(st.session_state['jogadores']):
        col = cols[i % 3]
        if col.button(jogador, key=f"btn_{jogador}_{tipo_evento}", use_container_width=True):
            registrar_evento(tipo_evento, equipa, jogador)
            st.rerun()
            
    st.divider()
    if st.button("Não especificar / Equipa Geral", type="secondary"):
        registrar_evento(tipo_evento, equipa, "Geral")
        st.rerun()

# --- Relógio Automático ---
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
st.title("⚽ ScoutMaster: Painel de Jogo")

# Sidebar
with st.sidebar:
    st.header("Configurações")
    equipa_casa = st.text_input("Minha Equipa", "Minha Equipa")
    equipa_fora = st.text_input("Adversário", "Adversário")
    
    with st.expander("Gerir Plantel"):
        novos_jogadores = st.text_area("Lista de Jogadores (um por linha)", 
                                       value="\n".join(st.session_state['jogadores']))
        if st.button("Atualizar Plantel"):
            st.session_state['jogadores'] = [nome.strip() for nome in novos_jogadores.split('\n') if nome.strip()]
            st.success("Plantel atualizado!")

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

# --- PLACAR ---
golos_casa = len([e for e in st.session_state['eventos'] if e['Evento'] == 'Golo' and e['Equipa'] == equipa_casa])
golos_fora = len([e for e in st.session_state['eventos'] if e['Evento'] == 'Golo' and e['Equipa'] == equipa_fora])

st.divider()
c1, c2, c3 = st.columns([1, 0.5, 1])
with c1: st.markdown(f"<h3 style='text-align:center;color:#4CAF50'>{equipa_casa}</h3><h1 style='text-align:center;font-size:50px'>{golos_casa}</h1>", unsafe_allow_html=True)
with c2: st.markdown("<br><h2 style='text-align:center'>VS</h2>", unsafe_allow_html=True)
with c3: st.markdown(f"<h3 style='text-align:center;color:#FF5252'>{equipa_fora}</h3><h1 style='text-align:center;font-size:50px'>{golos_fora}</h1>", unsafe_allow_html=True)
st.divider()

# --- Área de Ação ---
tab1, tab2, tab3 = st.tabs([f"🎮 {equipa_casa}", f"🛡️ {equipa_fora}", "📊 Relatórios"])

with tab1:
    st.info("💡 Clica para abrir a seleção de jogador")
    col1, col2, col3 = st.columns(3)
    
    # Nota: Para abrir o dialog, usamos 'if st.button' em vez de 'on_click'
    with col1:
        if st.button("⚽ GOLO", type="primary", use_container_width=True):
            selecionar_jogador("Golo", equipa_casa)
        if st.button("🎯 Remate à Baliza", use_container_width=True):
            selecionar_jogador("Remate à Baliza", equipa_casa)
            
    with col2:
        if st.button("❌ Passe Errado", use_container_width=True):
            selecionar_jogador("Passe Errado", equipa_casa)
        if st.button("🤕 Falta Sofrida", use_container_width=True):
            selecionar_jogador("Falta Sofrida", equipa_casa)
            
    with col3:
        if st.button("🚩 Canto", use_container_width=True):
            registrar_evento("Canto", equipa_casa, "Equipa") # Cantos normalmente não associamos a jogador específico aqui
        if st.button("🟡 Cartão Amarelo", use_container_width=True):
            selecionar_jogador("Cartão Amarelo", equipa_casa)

with tab2:
    colA, colB = st.columns(2)
    with colA:
        if st.button("Golo Sofrido", type="primary", use_container_width=True):
            registrar_evento("Golo", equipa_fora, "Adversário")
        if st.button("Remate Deles", use_container_width=True):
            registrar_evento("Remate", equipa_fora, "Adversário")
    with colB:
        if st.button("Falta Deles", use_container_width=True):
            registrar_evento("Falta Cometida", equipa_fora, "Adversário")

with tab3:
    if len(st.session_state['eventos']) > 0:
        df = pd.DataFrame(st.session_state['eventos'])
        
        # Filtro de Jogador
        jogadores_com_dados = df[df['Equipa'] == equipa_casa]['Jogador'].unique()
        filtro_jogador = st.selectbox("Filtrar por Jogador (Relatório Individual)", ["Todos"] + list(jogadores_com_dados))
        
        if filtro_jogador != "Todos":
            df_view = df[df['Jogador'] == filtro_jogador]
            st.success(f"A mostrar dados de: **{filtro_jogador}**")
        else:
            df_view = df

        # Estatísticas
        st.subheader("Resumo Estatístico")
        stats = df_view.pivot_table(index='Evento', columns='Equipa', aggfunc='size', fill_value=0)
        st.dataframe(stats, use_container_width=True)
        
        st.subheader("Timeline do Jogo")
        st.dataframe(
            df_view[['Minuto', 'Equipa', 'Jogador', 'Evento']].sort_values(by='Minuto', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório Completo", data=csv, file_name='scout_completo.csv', mime='text/csv')
    else:
        st.info("Aguarda pelo início do jogo...")
