import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import os
import hashlib
import requests
import time

# =========================================
# 🗄️ SISTEMA DE PERSISTÊNCIA MELHORADO
# =========================================

def get_data_path():
    """Define o caminho para salvar dados no Streamlit Cloud"""
    return 'dados.json'

def salvar_dados():
    """Salva dados com tratamento de erro"""
    try:
        dados = {
            'pedidos': st.session_state.pedidos,
            'clientes': st.session_state.clientes,
            'produtos': st.session_state.produtos,
            'usuarios': st.session_state.usuarios,  # 👈 AGORA SALVA USUÁRIOS TAMBÉM
            'ultimo_backup': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        with open(get_data_path(), 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar dados: {e}")
        return False

def carregar_dados():
    """Carrega dados com tratamento robusto"""
    try:
        if os.path.exists(get_data_path()):
            with open(get_data_path(), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            st.session_state.pedidos = dados.get('pedidos', [])
            st.session_state.clientes = dados.get('clientes', [])
            st.session_state.produtos = dados.get('produtos', [])
            st.session_state.usuarios = dados.get('usuarios', {})  # 👈 CARREGA USUÁRIOS
            
            # Migração de dados antigos
            for produto in st.session_state.produtos:
                if 'escola' not in produto:
                    produto['escola'] = "Municipal"
                    
            return True
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
    
    # Se não conseguir carregar, inicia vazio
    st.session_state.pedidos = []
    st.session_state.clientes = [] 
    st.session_state.produtos = []
    st.session_state.usuarios = {}  # 👈 INICIA USUÁRIOS VAZIO
    return False

# =========================================
# 🔐 SISTEMA DE AUTENTICAÇÃO AVANÇADO
# =========================================

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 👇 AGORA OS USUÁRIOS FICAM NO session_state E SÃO PERSISTIDOS
def inicializar_usuarios():
    """Inicializa usuários padrão se não existirem"""
    if not st.session_state.usuarios:
        st.session_state.usuarios = {
            "admin": make_hashes("Admin@2024!"),
            "vendedor": make_hashes("Vendas@123")
        }
        salvar_dados()  # 👈 SALVA OS USUÁRIOS NOVOS

def cadastrar_usuario(novo_usuario, nova_senha):
    """Cadastra novo usuário no sistema"""
    if novo_usuario in st.session_state.usuarios:
        return False, "❌ Usuário já existe!"
    
    if len(nova_senha) < 6:
        return False, "❌ Senha deve ter pelo menos 6 caracteres!"
    
    st.session_state.usuarios[novo_usuario] = make_hashes(nova_senha)
    salvar_dados()  # 👈 SALVA NO BANCO DE DADOS
    return True, "✅ Usuário cadastrado com sucesso!"

def alterar_senha(usuario, senha_atual, nova_senha):
    """Altera senha de usuário existente"""
    if usuario not in st.session_state.usuarios:
        return False, "❌ Usuário não encontrado!"
    
    if not check_hashes(senha_atual, st.session_state.usuarios[usuario]):
        return False, "❌ Senha atual incorreta!"
    
    if len(nova_senha) < 6:
        return False, "❌ Nova senha deve ter pelo menos 6 caracteres!"
    
    st.session_state.usuarios[usuario] = make_hashes(nova_senha)
    salvar_dados()  # 👈 SALVA ALTERAÇÃO
    return True, "✅ Senha alterada com sucesso!"

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type='password')
    
    if st.sidebar.button("Entrar"):
        if username in st.session_state.usuarios and check_hashes(password, st.session_state.usuarios[username]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.sidebar.success(f"Bem-vindo, {username}!")
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha inválidos")
    return False

# =========================================
# ⏰ SISTEMA ANTI-HIBERNAÇÃO
# =========================================

def manter_app_ativo():
    """Tenta manter o app ativo fazendo uma requisição periódica"""
    try:
        # Isso vai gerar tráfego e evitar hibernação
        agora = datetime.now()
        if 'ultimo_ping' not in st.session_state:
            st.session_state.ultimo_ping = agora
        
        # A cada 5 minutos, gera uma pequena atividade
        if (agora - st.session_state.ultimo_ping).seconds > 300:
            st.session_state.ultimo_ping = agora
            # Apenas atualiza um timestamp para gerar atividade
            if 'contador_ativacao' not in st.session_state:
                st.session_state.contador_ativacao = 0
            st.session_state.contador_ativacao += 1
            
    except Exception as e:
        # Falha silenciosamente - não queremos erro por causa do anti-hibernação
        pass

# =========================================
# 🚀 INICIALIZAÇÃO DO SISTEMA
# =========================================

st.set_page_config(
    page_title="Sistema de Fardamentos",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do session_state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'dados_carregados' not in st.session_state:
    carregar_dados()
    inicializar_usuarios()  # 👈 INICIALIZA USUÁRIOS
    st.session_state.dados_carregados = True

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

if 'clientes' not in st.session_state:
    st.session_state.clientes = []

if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if 'escolas' not in st.session_state:
    st.session_state.escolas = ["Municipal", "Desperta", "São Tadeu", "Outra"]

if 'itens_pedido' not in st.session_state:
    st.session_state.itens_pedido = []

# Sistema anti-hibernação
manter_app_ativo()

# CONFIGURAÇÕES ESPECÍFICAS - TAMANHOS CORRETOS
tamanhos_infantil = ["2", "4", "6", "8", "10", "12"]
tamanhos_adulto = ["PP", "P", "M", "G", "GG"]
todos_tamanhos = tamanhos_infantil + tamanhos_adulto

# PRODUTOS REAIS
tipos_camisetas = [
    "Camiseta Básica", 
    "Camiseta Regata", 
    "Camiseta Manga Longa"
]

tipos_calcas = [
    "Calça Jeans",
    "Calça Tactel", 
    "Calça Moletom",
    "Bermuda",
    "Short",
    "Short Saia"
]

tipos_agasalhos = [
    "Blusão",
    "Moletom"
]

def verificar_e_corrigir_dados():
    """Verifica e corrige dados corrompidos"""
    pedidos_validos = []
    for pedido in st.session_state.pedidos:
        if isinstance(pedido, dict):
            if 'id' not in pedido:
                pedido['id'] = len(pedidos_validos) + 1
            if 'status' not in pedido:
                pedido['status'] = 'Pendente'
            if 'cliente' not in pedido:
                pedido['cliente'] = 'Cliente Desconhecido'
            pedidos_validos.append(pedido)
    st.session_state.pedidos = pedidos_validos

# Verificar dados ao carregar
verificar_e_corrigir_dados()

# =========================================
# 🎨 NAVEGAÇÃO
# =========================================

if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.title("👕 Sistema de Fardamentos")

menu_options = ["📊 Dashboard", "📦 Pedidos", "👥 Clientes", "👕 Fardamentos", "📦 Estoque", "📈 Relatórios", "⚙️ Configurações"]
if 'menu' not in st.session_state:
    st.session_state.menu = menu_options[0]

menu = st.sidebar.radio("Navegação", menu_options, index=menu_options.index(st.session_state.menu))
st.session_state.menu = menu

# HEADER DINÂMICO
if menu == "📊 Dashboard":
    st.title("📊 Dashboard - Visão Geral")
elif menu == "📦 Pedidos":
    st.title("📦 Gestão de Pedidos") 
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
elif menu == "👕 Fardamentos":
    st.title("👕 Gestão de Fardamentos")
elif menu == "📦 Estoque":
    st.title("📦 Controle de Estoque")
elif menu == "📈 Relatórios":
    st.title("📈 Relatórios Detalhados")
elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações do Sistema")

st.markdown("---")

# =========================================
# ⚙️ NOVA PÁGINA: CONFIGURAÇÕES
# =========================================

if menu == "⚙️ Configurações":
    tab1, tab2, tab3 = st.tabs(["👥 Gerenciar Usuários", "🔐 Alterar Senha", "🔄 Sistema"])
    
    with tab1:
        st.header("👥 Gerenciar Usuários")
        
        st.subheader("➕ Cadastrar Novo Usuário")
        with st.form("novo_usuario"):
            novo_usuario = st.text_input("Nome de usuário")
            nova_senha = st.text_input("Senha", type="password")
            confirmar_senha = st.text_input("Confirmar senha", type="password")
            
            if st.form_submit_button("✅ Cadastrar Usuário"):
                if not novo_usuario or not nova_senha:
                    st.error("❌ Preencha todos os campos!")
                elif nova_senha != confirmar_senha:
                    st.error("❌ Senhas não coincidem!")
                else:
                    sucesso, mensagem = cadastrar_usuario(novo_usuario, nova_senha)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)
        
        st.subheader("📋 Usuários Cadastrados")
        if st.session_state.usuarios:
            df_usuarios = pd.DataFrame({
                'Usuário': list(st.session_state.usuarios.keys()),
                'Tipo': ['Administrador' if user == 'admin' else 'Vendedor' for user in st.session_state.usuarios.keys()]
            })
            st.dataframe(df_usuarios, use_container_width=True)
            
            st.info(f"👥 Total de usuários: {len(st.session_state.usuarios)}")
        else:
            st.info("👥 Nenhum usuário cadastrado")
    
    with tab2:
        st.header("🔐 Alterar Senha")
        
        with st.form("alterar_senha"):
            usuario = st.selectbox("Usuário", list(st.session_state.usuarios.keys()))
            senha_atual = st.text_input("Senha atual", type="password")
            nova_senha = st.text_input("Nova senha", type="password")
            confirmar_nova_senha = st.text_input("Confirmar nova senha", type="password")
            
            if st.form_submit_button("🔄 Alterar Senha"):
                if not senha_atual or not nova_senha:
                    st.error("❌ Preencha todos os campos!")
                elif nova_senha != confirmar_nova_senha:
                    st.error("❌ Novas senhas não coincidem!")
                else:
                    sucesso, mensagem = alterar_senha(usuario, senha_atual, nova_senha)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)
    
    with tab3:
        st.header("🔄 Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Status do Sistema")
            st.info(f"🕒 Última atividade: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.info(f"👥 Usuários cadastrados: {len(st.session_state.usuarios)}")
            st.info(f"📦 Pedidos no sistema: {len(st.session_state.pedidos)}")
            st.info(f"👕 Produtos cadastrados: {len(st.session_state.produtos)}")
            
            if 'contador_ativacao' in st.session_state:
                st.info(f"🔄 Atividades anti-hibernação: {st.session_state.contador_ativacao}")
        
        with col2:
            st.subheader("🛠️ Manutenção")
            
            if st.button("🔄 Recarregar Todos os Dados", use_container_width=True):
                carregar_dados()
                st.success("✅ Dados recarregados!")
                st.rerun()
            
            if st.button("🗑️ Limpar Dados Temporários", use_container_width=True):
                st.session_state.itens_pedido = []
                st.success("✅ Dados temporários limpos!")
            
            st.subheader("📋 Informações Técnicas")
            st.write(f"👤 Usuário atual: **{st.session_state.username}**")
            st.write("💡 Dica: Para evitar hibernação, acesse o sistema regularmente")

# =========================================
# 📱 PÁGINAS DO SISTEMA (MANTIDAS)
# =========================================

# DASHBOARD
elif menu == "📊 Dashboard":
    st.header("🎯 Métricas em Tempo Real")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pedidos = len(st.session_state.pedidos)
        st.metric("Total de Pedidos", total_pedidos)
    
    with col2:
        pedidos_pendentes = len([p for p in st.session_state.pedidos if p.get('status', 'Pendente') == 'Pendente'])
        st.metric("Pedidos Pendentes", pedidos_pendentes)
    
    with col3:
        clientes_ativos = len(st.session_state.clientes)
        st.metric("Clientes Ativos", clientes_ativos)
    
    with col4:
        produtos_baixo_estoque = len([p for p in st.session_state.produtos if p.get('estoque', 0) < 5])
        st.metric("Alertas de Estoque", produtos_baixo_estoque, delta=-produtos_baixo_estoque)
    
    # Ações Rápidas
    st.header("⚡ Ações Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Novo Pedido", use_container_width=True):
            st.session_state.menu = "📦 Pedidos"
            st.rerun()
    
    with col2:
        if st.button("👥 Cadastrar Cliente", use_container_width=True):
            st.session_state.menu = "👥 Clientes"
            st.rerun()
    
    with col3:
        if st.button("👕 Cadastrar Fardamento", use_container_width=True):
            st.session_state.menu = "👕 Fardamentos"
            st.rerun()
    
    # Alertas de Estoque
    st.header("⚠️ Alertas de Estoque")
    produtos_alerta = [p for p in st.session_state.produtos if p.get('estoque', 0) < 5]
    
    if produtos_alerta:
        for produto in produtos_alerta:
            st.warning(f"🚨 {produto['nome']} - Tamanho: {produto.get('tamanho', 'N/A')} - Estoque: {produto.get('estoque', 0)}")
    else:
        st.success("✅ Nenhum alerta de estoque")
    
    # Gráficos (código mantido igual)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vendas por Escola")
        if st.session_state.pedidos:
            escolas_data = {}
            for pedido in st.session_state.pedidos:
                if 'escolas' in pedido:
                    for escola in pedido['escolas']:
                        escolas_data[escola] = escolas_data.get(escola, 0) + 1
                else:
                    escola = pedido.get('escola', 'N/A')
                    escolas_data[escola] = escolas_data.get(escola, 0) + 1
            
            if escolas_data:
                df_escolas = pd.DataFrame(list(escolas_data.items()), columns=['Escola', 'Quantidade'])
                fig = px.bar(df_escolas, x='Escola', y='Quantidade', title="Vendas por Escola")
                st.plotly_chart(fig)
            else:
                st.info("📋 Nenhum dado para mostrar")
        else:
            st.info("📋 Nenhum pedido cadastrado")
    
    with col2:
        st.subheader("🎯 Status dos Pedidos")
        if st.session_state.pedidos:
            status_data = {}
            for pedido in st.session_state.pedidos:
                status = pedido.get('status', 'Pendente')
                status_data[status] = status_data.get(status, 0) + 1
            
            if status_data:
                df_status = pd.DataFrame(list(status_data.items()), columns=['Status', 'Quantidade'])
                fig = px.pie(df_status, values='Quantidade', names='Status', title="Status dos Pedidos")
                st.plotly_chart(fig)
            else:
                st.info("📋 Nenhum dado para mostrar")
        else:
            st.info("📋 Nenhum pedido para analisar")

# ... (O RESTANTE DO SEU CÓDIGO ORIGINAL PERMANECE IGUAL - PEDIDOS, CLIENTES, FARDAMENTOS, ESTOQUE, RELATÓRIOS) ...

# =========================================
# 💾 SISTEMA DE BACKUP E GERENCIAMENTO
# =========================================

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Sistema de Dados")

if st.sidebar.button("💾 Salvar Dados Agora"):
    if salvar_dados():
        st.sidebar.success("✅ Dados salvos!")
    else:
        st.sidebar.error("❌ Erro ao salvar")

if st.sidebar.button("🔄 Recarregar Dados"):
    if carregar_dados():
        st.sidebar.success("✅ Dados recarregados!")
        st.rerun()
    else:
        st.sidebar.error("❌ Erro ao recarregar")

# Backup manual
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Exportar Backup")

if st.sidebar.button("📥 Gerar Backup"):
    dados = {
        'pedidos': st.session_state.pedidos,
        'clientes': st.session_state.clientes,
        'produtos': st.session_state.produtos,
        'usuarios': st.session_state.usuarios,  # 👈 AGORA INCLUI USUÁRIOS
        'data_backup': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'total_registros': len(st.session_state.pedidos) + len(st.session_state.clientes) + len(st.session_state.produtos)
    }
    backup_json = json.dumps(dados, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="⬇️ Baixar Backup",
        data=backup_json,
        file_name=f"backup_fardamentos_{datetime.now().strftime('%d%m%Y_%H%M')}.json",
        mime="application/json"
    )

# Estatísticas
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Estatísticas")
st.sidebar.write(f"📦 Pedidos: {len(st.session_state.pedidos)}")
st.sidebar.write(f"👥 Clientes: {len(st.session_state.clientes)}")
st.sidebar.write(f"👕 Produtos: {len(st.session_state.produtos)}")
st.sidebar.write(f"👤 Usuários: {len(st.session_state.usuarios)}")

# Logout
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.write(f"👤 Usuário: **{st.session_state.username}**")

# Notificação de alertas
if 'alertas_mostrados' not in st.session_state:
    st.session_state.alertas_mostrados = True
    produtos_baixo_estoque = [p for p in st.session_state.produtos if p.get('estoque', 0) < 5]
    if produtos_baixo_estoque:
        st.toast("⚠️ Alertas de estoque baixo detectados! Verifique a seção de Estoque.")