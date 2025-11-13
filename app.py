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
# 🗄️ SISTEMA PRINCIPAL
# =========================================

# Importar configurações
try:
    from database.supabase_config import (
        salvar_fardamento, buscar_fardamentos,
        atualizar_fardamento, excluir_fardamento, salvar_pedido,
        buscar_pedidos, salvar_cliente, buscar_clientes, sistema_hibrido
    )
except Exception as e:
    st.sidebar.error("❌ Erro ao carregar sistema")

# Status do sistema
status, _ = sistema_hibrido()
st.sidebar.success(status)
# =========================================
# 🗄️ SISTEMA DE PERSISTÊNCIA MELHORADO
# =========================================

def get_data_path():
    """Define o caminho para salvar dados no Streamlit Cloud"""
    return 'data/dados_backup.json'

def salvar_dados():
    """Salva dados com tratamento de erro"""
    try:
        dados = {
            'pedidos': st.session_state.pedidos,
            'clientes': st.session_state.clientes,
            'produtos': st.session_state.produtos,
            'usuarios': st.session_state.usuarios,
            'ultimo_backup': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        # Garantir que pasta data existe
        os.makedirs("data", exist_ok=True)
        
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
            st.session_state.usuarios = dados.get('usuarios', {})
            
            return True
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
    
    # Se não conseguir carregar, inicia vazio
    st.session_state.pedidos = []
    st.session_state.clientes = [] 
    st.session_state.produtos = []
    st.session_state.usuarios = {}
    return False

# =========================================
# 🔐 SISTEMA DE AUTENTICAÇÃO AVANÇADO
# =========================================

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def inicializar_usuarios():
    """Inicializa usuários padrão se não existirem"""
    if not st.session_state.usuarios:
        st.session_state.usuarios = {
            "admin": make_hashes("Admin@2024!"),
            "vendedor": make_hashes("Vendas@123")
        }
        salvar_dados()

def cadastrar_usuario(novo_usuario, nova_senha):
    """Cadastra novo usuário no sistema"""
    if novo_usuario in st.session_state.usuarios:
        return False, "❌ Usuário já existe!"
    
    if len(nova_senha) < 6:
        return False, "❌ Senha deve ter pelo menos 6 caracteres!"
    
    st.session_state.usuarios[novo_usuario] = make_hashes(nova_senha)
    salvar_dados()
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
    salvar_dados()
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
        agora = datetime.now()
        if 'ultimo_ping' not in st.session_state:
            st.session_state.ultimo_ping = agora
        
        # A cada 5 minutos, gera uma pequena atividade
        if (agora - st.session_state.ultimo_ping).seconds > 300:
            st.session_state.ultimo_ping = agora
            if 'contador_ativacao' not in st.session_state:
                st.session_state.contador_ativacao = 0
            st.session_state.contador_ativacao += 1
            
    except Exception:
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
    inicializar_usuarios()
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
# ⚙️ PÁGINA: CONFIGURAÇÕES
# =========================================

if menu == "⚙️ Configurações":
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Gerenciar Usuários", "🔐 Alterar Senha", "🗄️ Banco de Dados", "🔄 Sistema"])
    
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
        st.header("🗄️ Banco de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Status do Sistema")
            if SUPABASE_DISPONIVEL:
                status, conectado = sistema_hibrido()
                if conectado:
                    st.success("✅ Supabase Conectado")
                    
                    # Testar funcionalidades
                    if st.button("🧪 Testar Funcionalidades"):
                        try:
                            fardamentos = buscar_fardamentos()
                            st.success(f"✅ Funcionando! {len(fardamentos)} fardamentos no banco")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                else:
                    st.warning("⚠️ Supabase com problemas")
            else:
                st.info("📱 Modo Local Ativo")
                st.write("Dados salvos temporariamente na sessão")
        
        with col2:
            st.subheader("🔄 Migração de Dados")
            
            if st.button("🚀 Migrar para Supabase", use_container_width=True):
                if SUPABASE_DISPONIVEL:
                    with st.spinner("Migrando dados locais..."):
                        # Migrar produtos
                        produtos_migrados = 0
                        for produto in st.session_state.produtos:
                            if salvar_fardamento(
                                nome=produto.get('nome', ''),
                                tamanho=produto.get('tamanho', ''),
                                quantidade=produto.get('quantidade', 0),
                                categoria=produto.get('categoria', ''),
                                responsavel=produto.get('responsavel', ''),
                                observacoes=produto.get('observacoes', '')
                            ):
                                produtos_migrados += 1
                        
                        st.success(f"✅ {produtos_migrados} produtos migrados!")
                else:
                    st.error("❌ Supabase não disponível")
            
            st.subheader("💾 Backup")
            if st.button("📥 Exportar Backup Local", use_container_width=True):
                dados = {
                    'pedidos': st.session_state.pedidos,
                    'clientes': st.session_state.clientes,
                    'produtos': st.session_state.produtos,
                    'usuarios': st.session_state.usuarios,
                    'data_backup': datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                backup_json = json.dumps(dados, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ Baixar Backup",
                    data=backup_json,
                    file_name=f"backup_fardamentos_{datetime.now().strftime('%d%m%Y_%H%M')}.json",
                    mime="application/json"
                )
    
    with tab4:
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
            st.write(f"🗄️ Banco: {'Supabase' if SUPABASE_DISPONIVEL else 'Local'}")
            st.write("💡 Dica: Para evitar hibernação, acesse o sistema regularmente")

# =========================================
# 📊 DASHBOARD
# =========================================

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
        produtos_baixo_estoque = len([p for p in st.session_state.produtos if p.get('quantidade', 0) < 5])
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
    produtos_alerta = [p for p in st.session_state.produtos if p.get('quantidade', 0) < 5]
    
    if produtos_alerta:
        for produto in produtos_alerta:
            st.warning(f"🚨 {produto['nome']} - Tamanho: {produto.get('tamanho', 'N/A')} - Estoque: {produto.get('quantidade', 0)}")
    else:
        st.success("✅ Nenhum alerta de estoque")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vendas por Escola")
        if st.session_state.pedidos:
            escolas_data = {}
            for pedido in st.session_state.pedidos:
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

# =========================================
# 👕 PÁGINA: FARDAMENTOS (CORRIGIDA)
# =========================================

elif menu == "👕 Fardamentos":
    st.header("👕 Gestão de Fardamentos")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Fardamento", "📋 Lista de Fardamentos"])
    
    with tab1:
        st.subheader("➕ Cadastrar Novo Fardamento")
        
        with st.form("novo_fardamento"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Fardamento*")
                tamanho = st.selectbox("Tamanho*", todos_tamanhos)
                quantidade = st.number_input("Quantidade*", min_value=0, value=0)
            
            with col2:
                categoria = st.selectbox("Categoria*", ["Camiseta", "Camiseta Regata", "Calça", "Short", "Short Saia"])
                escola = st.selectbox("Escola*", st.session_state.escolas)
                observacoes = st.text_area("Observações")
            
            submitted = st.form_submit_button("💾 Salvar Fardamento")
            if submitted:
                if nome and tamanho and quantidade >= 0 and categoria and escola:
                    salvar_fardamento(
                        nome=nome,
                        tamanho=tamanho,
                        quantidade=quantidade,
                        categoria=categoria,
                        escola=escola,
                        observacoes=observacoes
                    )
                    st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios!")
    
    with tab2:
        st.subheader("📋 Fardamentos Cadastrados")
        
        if st.session_state.produtos:
            df_local = pd.DataFrame(st.session_state.produtos)
            st.dataframe(df_local, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Fardamentos", len(st.session_state.produtos))
            with col2:
                total_estoque = sum(p.get('quantidade', 0) for p in st.session_state.produtos)
                st.metric("Total em Estoque", total_estoque)
            with col3:
                baixo_estoque = len([p for p in st.session_state.produtos if p.get('quantidade', 0) < 5])
                st.metric("Baixo Estoque", baixo_estoque)
            with col4:
                # Fardamentos por escola
                escolas_count = df_local['escola'].value_counts()
                escola_mais = escolas_count.index[0] if not escolas_count.empty else "Nenhuma"
                st.metric("Escola com Mais", escola_mais)
        else:
            st.info("📋 Nenhum fardamento cadastrado")
# =========================================
# 📦 PÁGINA: PEDIDOS (CORRIGIDA)
# =========================================

elif menu == "📦 Pedidos":
    st.header("📦 Gestão de Pedidos")
    
    tab1, tab2 = st.tabs(["➕ Novo Pedido", "📋 Pedidos Cadastrados"])
    
    with tab1:
        st.subheader("➕ Novo Pedido")
        
        # Seção para adicionar itens (FORA do formulário principal)
        st.subheader("👕 Adicionar Itens ao Pedido")
        col1, col2, col3 = st.columns(3)
        with col1:
            item_nome = st.selectbox("Fardamento", ["Camiseta Básica", "Camiseta Regata", "Calça Jeans", "Short", "Short Saia"])
        with col2:
            item_tamanho = st.selectbox("Tamanho", todos_tamanhos)
        with col3:
            item_quantidade = st.number_input("Quantidade", min_value=1, value=1)
        
        if st.button("➕ Adicionar Item", key="add_item"):
            novo_item = {
                'nome': item_nome,
                'tamanho': item_tamanho,
                'quantidade': item_quantidade
            }
            st.session_state.itens_pedido.append(novo_item)
            st.success(f"✅ {item_quantidade}x {item_nome} ({item_tamanho}) adicionado!")
            st.rerun()
        
        # Mostrar itens adicionados
        if st.session_state.itens_pedido:
            st.subheader("📋 Itens no Pedido")
            df_itens = pd.DataFrame(st.session_state.itens_pedido)
            st.dataframe(df_itens, use_container_width=True)
            
            total_itens = sum(item['quantidade'] for item in st.session_state.itens_pedido)
            st.info(f"📦 Total de itens: {total_itens}")
            
            # Botão para limpar itens
            if st.button("🗑️ Limpar Todos os Itens", type="secondary"):
                st.session_state.itens_pedido = []
                st.rerun()
        
        # Formulário principal do pedido
        with st.form("novo_pedido"):
            st.subheader("📝 Informações do Pedido")
            
            col1, col2 = st.columns(2)
            with col1:
                cliente = st.text_input("Cliente*")
                escola = st.selectbox("Escola*", st.session_state.escolas)
            with col2:
                data_entrega = st.date_input("Data de Entrega", min_value=date.today())
                status = st.selectbox("Status", ["Pendente", "Em produção", "Pronto", "Entregue"])
            
            observacoes = st.text_area("Observações do Pedido")
            
            submitted = st.form_submit_button("💾 Salvar Pedido")
            if submitted:
                if cliente and escola and st.session_state.itens_pedido:
                    novo_pedido = {
                        'cliente': cliente,
                        'escola': escola,
                        'data_pedido': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'data_entrega': data_entrega.strftime("%d/%m/%Y"),
                        'status': status,
                        'itens': st.session_state.itens_pedido.copy(),
                        'observacoes': observacoes,
                        'total_itens': total_itens
                    }
                    
                    if salvar_pedido(novo_pedido):
                        st.session_state.itens_pedido = []
                        st.rerun()
                else:
                    st.error("❌ Preencha cliente, escola e adicione itens!")
    
    with tab2:
        st.subheader("📋 Pedidos Cadastrados")
        
        if st.session_state.pedidos:
            df_local = pd.DataFrame(st.session_state.pedidos)
            st.dataframe(df_local, use_container_width=True)
            
            # Estatísticas de pedidos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Pedidos", len(st.session_state.pedidos))
            with col2:
                pedidos_pendentes = len([p for p in st.session_state.pedidos if p.get('status') == 'Pendente'])
                st.metric("Pedidos Pendentes", pedidos_pendentes)
            with col3:
                total_itens_pedidos = sum(p.get('total_itens', 0) for p in st.session_state.pedidos)
                st.metric("Total de Itens", total_itens_pedidos)
        else:
            st.info("📋 Nenhum pedido cadastrado")
# =========================================
# 👥 PÁGINA: CLIENTES
# =========================================

elif menu == "👥 Clientes":
    st.header("👥 Gestão de Clientes")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Cliente", "📋 Clientes Cadastrados"])
    
    with tab1:
        st.subheader("➕ Cadastrar Novo Cliente")
        
        with st.form("novo_cliente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome*")
                telefone = st.text_input("Telefone")
                escola = st.selectbox("Escola", st.session_state.escolas)
            
            with col2:
                email = st.text_input("Email")
                responsavel = st.text_input("Responsável")
                observacoes = st.text_area("Observações")
            
            if st.form_submit_button("💾 Salvar Cliente"):
                if nome:
                    novo_cliente = {
                        'id': len(st.session_state.clientes) + 1,
                        'nome': nome,
                        'telefone': telefone,
                        'email': email,
                        'escola': escola,
                        'responsavel': responsavel,
                        'observacoes': observacoes,
                        'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    if SUPABASE_DISPONIVEL:
                        sucesso = salvar_cliente(novo_cliente)
                        if sucesso:
                            st.rerun()
                    else:
                        st.session_state.clientes.append(novo_cliente)
                        salvar_dados()
                        st.success("✅ Cliente cadastrado localmente!")
                        st.rerun()
                else:
                    st.error("❌ Preencha o nome do cliente!")
    
    with tab2:
        st.subheader("📋 Clientes Cadastrados")
        
        if SUPABASE_DISPONIVEL:
            try:
                clientes_df = buscar_clientes()
                if not clientes_df.empty:
                    st.dataframe(clientes_df, use_container_width=True)
                else:
                    st.info("📋 Nenhum cliente cadastrado no Supabase")
            except Exception as e:
                st.error(f"❌ Erro ao carregar clientes: {e}")
                if st.session_state.clientes:
                    df_local = pd.DataFrame(st.session_state.clientes)
                    st.dataframe(df_local, use_container_width=True)
                else:
                    st.info("📋 Nenhum cliente cadastrado")
        else:
            if st.session_state.clientes:
                df_local = pd.DataFrame(st.session_state.clientes)
                st.dataframe(df_local, use_container_width=True)
            else:
                st.info("📋 Nenhum cliente cadastrado")

# =========================================
# 📦 PÁGINA: ESTOQUE
# =========================================

elif menu == "📦 Estoque":
    st.header("📦 Controle de Estoque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Estoque Atual")
        if st.session_state.produtos:
            df_estoque = pd.DataFrame(st.session_state.produtos)
            st.dataframe(df_estoque, use_container_width=True)
        else:
            st.info("📋 Nenhum produto em estoque")
    
    with col2:
        st.subheader("🔄 Movimentações")
        
        with st.form("movimentacao_estoque"):
            tipo = st.radio("Tipo", ["Entrada", "Saída"])
            produto = st.selectbox("Produto", [p['nome'] for p in st.session_state.produtos] if st.session_state.produtos else [])
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            motivo = st.text_input("Motivo")
            
            if st.form_submit_button("💾 Registrar Movimentação"):
                st.success(f"✅ {tipo} de {quantidade} unidades registrada!")
    
    st.subheader("📈 Estatísticas de Estoque")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_produtos = len(st.session_state.produtos)
        st.metric("Total de Produtos", total_produtos)
    
    with col2:
        total_estoque = sum(p.get('quantidade', 0) for p in st.session_state.produtos)
        st.metric("Total em Estoque", total_estoque)
    
    with col3:
        baixo_estoque = len([p for p in st.session_state.produtos if p.get('quantidade', 0) < 5])
        st.metric("Produtos com Estoque Baixo", baixo_estoque)

# =========================================
# 📈 PÁGINA: RELATÓRIOS
# =========================================

elif menu == "📈 Relatórios":
    st.header("📈 Relatórios Detalhados")
    
    tab1, tab2, tab3 = st.tabs(["📊 Vendas", "👕 Produtos", "👥 Clientes"])
    
    with tab1:
        st.subheader("📊 Relatório de Vendas")
        
        if st.session_state.pedidos:
            # Vendas por escola
            escolas_vendas = {}
            for pedido in st.session_state.pedidos:
                escola = pedido.get('escola', 'N/A')
                total_itens = pedido.get('total_itens', 0)
                escolas_vendas[escola] = escolas_vendas.get(escola, 0) + total_itens
            
            if escolas_vendas:
                df_vendas = pd.DataFrame(list(escolas_vendas.items()), columns=['Escola', 'Total de Itens'])
                fig = px.bar(df_vendas, x='Escola', y='Total de Itens', title="Vendas por Escola")
                st.plotly_chart(fig)
        
        st.subheader("📋 Resumo de Pedidos")
        if st.session_state.pedidos:
            df_pedidos = pd.DataFrame(st.session_state.pedidos)
            st.dataframe(df_pedidos, use_container_width=True)
    
    with tab2:
        st.subheader("👕 Relatório de Produtos")
        
        if st.session_state.produtos:
            df_produtos = pd.DataFrame(st.session_state.produtos)
            
            # Produtos por categoria
            categorias = df_produtos['categoria'].value_counts()
            fig = px.pie(values=categorias.values, names=categorias.index, title="Produtos por Categoria")
            st.plotly_chart(fig)
            
            st.dataframe(df_produtos, use_container_width=True)
    
    with tab3:
        st.subheader("👥 Relatório de Clientes")
        
        if st.session_state.clientes:
            df_clientes = pd.DataFrame(st.session_state.clientes)
            
            # Clientes por escola
            escolas_clientes = df_clientes['escola'].value_counts()
            fig = px.bar(x=escolas_clientes.index, y=escolas_clientes.values, title="Clientes por Escola")
            st.plotly_chart(fig)
            
            st.dataframe(df_clientes, use_container_width=True)

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
        'usuarios': st.session_state.usuarios,
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
    produtos_baixo_estoque = [p for p in st.session_state.produtos if p.get('quantidade', 0) < 5]
    if produtos_baixo_estoque:
        st.toast("⚠️ Alertas de estoque baixo detectados! Verifique a seção de Estoque.")
