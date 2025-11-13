import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os
import hashlib
import requests
import time

# =========================================
# 🗄️ SISTEMA AVANÇADO DE FARDAMENTOS
# =========================================

# Importar configurações
try:
    from database.supabase_config import (
        salvar_fardamento, buscar_fardamentos, atualizar_estoque,
        excluir_fardamento, salvar_pedido, buscar_pedidos, atualizar_status_pedido,
        salvar_cliente, buscar_clientes, sistema_hibrido, registrar_movimentacao,
        buscar_movimentacoes, gerar_relatorio_estoque, gerar_estatisticas,
        buscar_historico, criar_tabelas_iniciais
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
            'movimentacoes': st.session_state.get('movimentacoes', []),
            'historico': st.session_state.get('historico', []),
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
            st.session_state.movimentacoes = dados.get('movimentacoes', [])
            st.session_state.historico = dados.get('historico', [])
            
            return True
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
    
    # Se não conseguir carregar, inicia vazio
    st.session_state.pedidos = []
    st.session_state.clientes = [] 
    st.session_state.produtos = []
    st.session_state.usuarios = {}
    st.session_state.movimentacoes = []
    st.session_state.historico = []
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
    page_title="Sistema de Fardamentos - Premium",
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
    criar_tabelas_iniciais()
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

# CATEGORIAS ATUALIZADAS
categorias_fardamento = ["Camiseta", "Camiseta Regata", "Calça", "Short", "Short Saia"]

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
# 🎨 NAVEGAÇÃO PREMIUM
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
# 📊 DASHBOARD PREMIUM
# =========================================

if menu == "📊 Dashboard":
    # Métricas em tempo real
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
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        if st.button("📊 Ver Relatórios", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"
            st.rerun()
    
    # Alertas de Estoque
    st.header("⚠️ Alertas de Estoque")
    produtos_alerta = [p for p in st.session_state.produtos if p.get('quantidade', 0) < 5]
    
    if produtos_alerta:
        for produto in produtos_alerta:
            cor = "🔴" if produto.get('quantidade', 0) == 0 else "🟡"
            st.warning(f"{cor} **{produto['nome']}** - Tamanho: {produto.get('tamanho', 'N/A')} - Estoque: {produto.get('quantidade', 0)} - Categoria: {produto.get('categoria', 'N/A')}")
    else:
        st.success("✅ Nenhum alerta de estoque")
    
    # Gráficos Dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vendas por Escola")
        if st.session_state.pedidos:
            escolas_data = {}
            for pedido in st.session_state.pedidos:
                escola = pedido.get('escola', 'N/A')
                total_itens = pedido.get('total_itens', 1)
                escolas_data[escola] = escolas_data.get(escola, 0) + total_itens
            
            if escolas_data:
                df_escolas = pd.DataFrame(list(escolas_data.items()), columns=['Escola', 'Quantidade'])
                fig = px.bar(df_escolas, x='Escola', y='Quantidade', title="Vendas por Escola", color='Quantidade')
                st.plotly_chart(fig, use_container_width=True)
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
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📋 Nenhum dado para mostrar")
        else:
            st.info("📋 Nenhum pedido para analisar")
    
    # Últimas Atividades
    st.header("📋 Últimas Atividades")
    historico = buscar_historico(10)
    if not historico.empty:
        for _, item in historico.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{item['tipo']}** - {item['detalhes']}")
                with col2:
                    st.caption(item['data'])
                st.divider()
    else:
        st.info("📝 Nenhuma atividade recente")

# =========================================
# 👕 PÁGINA: FARDAMENTOS PREMIUM
# =========================================

elif menu == "👕 Fardamentos":
    st.header("👕 Gestão de Fardamentos")
    
    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar Fardamento", "📋 Lista de Fardamentos", "🔍 Busca Avançada"])
    
    with tab1:
        st.subheader("➕ Cadastrar Novo Fardamento")
        
        with st.form("novo_fardamento"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Fardamento*", placeholder="Ex: Camiseta Básica Branca")
                tamanho = st.selectbox("Tamanho*", todos_tamanhos)
                quantidade = st.number_input("Quantidade*", min_value=0, value=0, step=1)
            
            with col2:
                categoria = st.selectbox("Categoria*", categorias_fardamento)
                escola = st.selectbox("Escola*", st.session_state.escolas)
                observacoes = st.text_area("Observações", placeholder="Detalhes, cor, material...")
            
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
        
        # Filtros rápidos
        col1, col2 = st.columns(2)
        with col1:
            filtro_escola = st.selectbox("Filtrar por Escola", ["Todas"] + st.session_state.escolas)
        with col2:
            filtro_categoria = st.selectbox("Filtrar por Categoria", ["Todas"] + categorias_fardamento)
        
        fardamentos_df = buscar_fardamentos(
            filtro_escola if filtro_escola != "Todas" else None,
            filtro_categoria if filtro_categoria != "Todas" else None
        )
        
        if not fardamentos_df.empty:
            # Formatar DataFrame para melhor visualização
            df_display = fardamentos_df[['id', 'nome', 'categoria', 'tamanho', 'quantidade', 'escola', 'data_cadastro']]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Fardamentos", len(fardamentos_df))
            with col2:
                total_estoque = fardamentos_df['quantidade'].sum()
                st.metric("Total em Estoque", total_estoque)
            with col3:
                baixo_estoque = len(fardamentos_df[fardamentos_df['quantidade'] < 5])
                st.metric("Baixo Estoque", baixo_estoque)
            with col4:
                escola_mais = fardamentos_df['escola'].value_counts().index[0] if not fardamentos_df.empty else "Nenhuma"
                st.metric("Escola com Mais", escola_mais)
        else:
            st.info("📋 Nenhum fardamento cadastrado")
    
    with tab3:
        st.subheader("🔍 Busca e Edição Avançada")
        
        if st.session_state.produtos:
            # Seletor de fardamento para edição
            fardamentos_opcoes = [f"{p['id']} - {p['nome']} ({p['tamanho']}) - {p['escola']}" for p in st.session_state.produtos]
            fardamento_selecionado = st.selectbox("Selecione um fardamento para editar:", fardamentos_opcoes)
            
            if fardamento_selecionado:
                fardamento_id = int(fardamento_selecionado.split(" - ")[0])
                fardamento = next((p for p in st.session_state.produtos if p['id'] == fardamento_id), None)
                
                if fardamento:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Informações Atuais:**")
                        st.write(f"**Nome:** {fardamento['nome']}")
                        st.write(f"**Categoria:** {fardamento['categoria']}")
                        st.write(f"**Tamanho:** {fardamento['tamanho']}")
                        st.write(f"**Escola:** {fardamento['escola']}")
                        st.write(f"**Estoque Atual:** {fardamento['quantidade']}")
                    
                    with col2:
                        st.write("**Ações Rápidas:**")
                        nova_quantidade = st.number_input("Nova Quantidade", value=fardamento['quantidade'], min_value=0)
                        motivo = st.text_input("Motivo da Alteração")
                        
                        if st.button("🔄 Atualizar Estoque"):
                            if atualizar_estoque(fardamento_id, nova_quantidade, motivo):
                                st.rerun()
                        
                        if st.button("🗑️ Excluir Fardamento", type="secondary"):
                            if excluir_fardamento(fardamento_id):
                                st.rerun()
        else:
            st.info("📋 Nenhum fardamento cadastrado para editar")

# =========================================
# 📦 PÁGINA: PEDIDOS PREMIUM
# =========================================

elif menu == "📦 Pedidos":
    st.header("📦 Gestão de Pedidos")
    
    tab1, tab2, tab3 = st.tabs(["➕ Novo Pedido", "📋 Pedidos Cadastrados", "🔄 Gerenciar Pedidos"])
    
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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Adicionar Item", use_container_width=True, key="add_item"):
                novo_item = {
                    'nome': item_nome,
                    'tamanho': item_tamanho,
                    'quantidade': item_quantidade
                }
                st.session_state.itens_pedido.append(novo_item)
                st.success(f"✅ {item_quantidade}x {item_nome} ({item_tamanho}) adicionado!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Limpar Todos os Itens", use_container_width=True, type="secondary"):
                st.session_state.itens_pedido = []
                st.rerun()
        
        # Mostrar itens adicionados
        if st.session_state.itens_pedido:
            st.subheader("📋 Itens no Pedido")
            df_itens = pd.DataFrame(st.session_state.itens_pedido)
            st.dataframe(df_itens, use_container_width=True, hide_index=True)
            
            total_itens = sum(item['quantidade'] for item in st.session_state.itens_pedido)
            st.info(f"📦 Total de itens no pedido: **{total_itens}**")
        
        # Formulário principal do pedido
        with st.form("novo_pedido"):
            st.subheader("📝 Informações do Pedido")
            
            col1, col2 = st.columns(2)
            with col1:
                cliente = st.text_input("Cliente*", placeholder="Nome do cliente ou escola")
                escola = st.selectbox("Escola*", st.session_state.escolas)
            with col2:
                data_entrega = st.date_input("Data de Entrega", min_value=date.today())
                status = st.selectbox("Status", ["Pendente", "Em produção", "Pronto", "Entregue"])
            
            observacoes = st.text_area("Observações do Pedido", placeholder="Instruções especiais, endereço...")
            
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
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.selectbox("Filtrar por Status", ["Todos", "Pendente", "Em produção", "Pronto", "Entregue"])
        with col2:
            filtro_escola = st.selectbox("Filtrar por Escola", ["Todas"] + st.session_state.escolas)
        
        pedidos_df = buscar_pedidos(
            filtro_status if filtro_status != "Todos" else None,
            filtro_escola if filtro_escola != "Todas" else None
        )
        
        if not pedidos_df.empty:
            # DataFrame simplificado para visualização
            colunas = ['id', 'cliente', 'escola', 'status', 'data_pedido', 'data_entrega', 'total_itens']
            colunas_disponiveis = [col for col in colunas if col in pedidos_df.columns]
            
            st.dataframe(pedidos_df[colunas_disponiveis], use_container_width=True, hide_index=True)
            
            # Estatísticas de pedidos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Pedidos", len(pedidos_df))
            with col2:
                pedidos_pendentes = len(pedidos_df[pedidos_df['status'] == 'Pendente'])
                st.metric("Pedidos Pendentes", pedidos_pendentes)
            with col3:
                total_itens_pedidos = pedidos_df['total_itens'].sum()
                st.metric("Total de Itens", total_itens_pedidos)
        else:
            st.info("📋 Nenhum pedido cadastrado")
    
    with tab3:
        st.subheader("🔄 Gerenciar Pedidos")
        
        if st.session_state.pedidos:
            # Lista de pedidos para gerenciamento
            for pedido in st.session_state.pedidos:
                with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} ({pedido['status']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido['cliente']}")
                        st.write(f"**Escola:** {pedido['escola']}")
                        st.write(f"**Data do Pedido:** {pedido['data_pedido']}")
                        st.write(f"**Data de Entrega:** {pedido['data_entrega']}")
                    
                    with col2:
                        st.write(f"**Status:** {pedido['status']}")
                        st.write(f"**Total de Itens:** {pedido['total_itens']}")
                        
                        # Alterar status
                        novo_status = st.selectbox(
                            "Alterar Status",
                            ["Pendente", "Em produção", "Pronto", "Entregue"],
                            index=["Pendente", "Em produção", "Pronto", "Entregue"].index(pedido['status']),
                            key=f"status_{pedido['id']}"
                        )
                        
                        if st.button("🔄 Atualizar Status", key=f"btn_{pedido['id']}"):
                            if atualizar_status_pedido(pedido['id'], novo_status):
                                st.rerun()
                    
                    # Itens do pedido
                    st.write("**Itens do Pedido:**")
                    if 'itens' in pedido and pedido['itens']:
                        df_itens = pd.DataFrame(pedido['itens'])
                        st.dataframe(df_itens, use_container_width=True, hide_index=True)
        else:
            st.info("📋 Nenhum pedido para gerenciar")

# =========================================
# 👥 PÁGINA: CLIENTES PREMIUM
# =========================================

elif menu == "👥 Clientes":
    st.header("👥 Gestão de Clientes")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Cliente", "📋 Clientes Cadastrados"])
    
    with tab1:
        st.subheader("➕ Cadastrar Novo Cliente")
        
        with st.form("novo_cliente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome*", placeholder="Nome completo ou razão social")
                telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
                escola = st.selectbox("Escola", st.session_state.escolas)
            
            with col2:
                email = st.text_input("Email", placeholder="cliente@email.com")
                responsavel = st.text_input("Responsável", placeholder="Nome do responsável")
                observacoes = st.text_area("Observações", placeholder="Informações adicionais...")
            
            submitted = st.form_submit_button("💾 Salvar Cliente")
            if submitted:
                if nome:
                    novo_cliente = {
                        'nome': nome,
                        'telefone': telefone,
                        'email': email,
                        'escola': escola,
                        'responsavel': responsavel,
                        'observacoes': observacoes
                    }
                    
                    if salvar_cliente(novo_cliente):
                        st.rerun()
                else:
                    st.error("❌ Preencha o nome do cliente!")
    
    with tab2:
        st.subheader("📋 Clientes Cadastrados")
        
        # Filtro por escola
        filtro_escola = st.selectbox("Filtrar por Escola", ["Todas"] + st.session_state.escolas)
        
        clientes_df = buscar_clientes(filtro_escola if filtro_escola != "Todas" else None)
        
        if not clientes_df.empty:
            st.dataframe(clientes_df, use_container_width=True, hide_index=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(clientes_df))
            with col2:
                escola_mais = clientes_df['escola'].value_counts().index[0] if not clientes_df.empty else "Nenhuma"
                st.metric("Escola com Mais", escola_mais)
            with col3:
                clientes_com_email = len(clientes_df[clientes_df['email'].notna() & (clientes_df['email'] != '')])
                st.metric("Com Email", clientes_com_email)
        else:
            st.info("📋 Nenhum cliente cadastrado")

# =========================================
# 📦 PÁGINA: ESTOQUE PREMIUM
# =========================================

elif menu == "📦 Estoque":
    st.header("📦 Controle de Estoque")
    
    tab1, tab2, tab3 = st.tabs(["📊 Estoque Atual", "🔄 Movimentações", "📈 Estatísticas"])
    
    with tab1:
        st.subheader("📊 Estoque Atual")
        
        relatorio_df = gerar_relatorio_estoque()
        
        if not relatorio_df.empty:
            # Colorir o DataFrame baseado no status
            def color_status(val):
                if val == 'ESGOTADO':
                    return 'color: red; font-weight: bold'
                elif val == 'BAIXO':
                    return 'color: orange; font-weight: bold'
                elif val == 'MEDIO':
                    return 'color: blue'
                else:
                    return 'color: green'
            
            styled_df = relatorio_df[['id', 'nome', 'categoria', 'tamanho', 'quantidade', 'escola', 'status_estoque']].style.applymap(
                color_status, subset=['status_estoque']
            )
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Gráfico de estoque por categoria
            st.subheader("📊 Distribuição por Categoria")
            estoque_por_categoria = relatorio_df.groupby('categoria')['quantidade'].sum().reset_index()
            fig = px.pie(estoque_por_categoria, values='quantidade', names='categoria', title="Estoque por Categoria")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📋 Nenhum produto em estoque")
    
    with tab2:
        st.subheader("🔄 Movimentações de Estoque")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Entrada de Estoque")
            with st.form("entrada_estoque"):
                fardamento_id = st.selectbox(
                    "Fardamento",
                    [f"{p['id']} - {p['nome']} ({p['tamanho']})" for p in st.session_state.produtos],
                    key="entrada"
                )
                quantidade_entrada = st.number_input("Quantidade", min_value=1, value=1, key="qtd_entrada")
                responsavel_entrada = st.text_input("Responsável", value=st.session_state.username)
                observacao_entrada = st.text_input("Observação", placeholder="Compra, doação...")
                
                if st.form_submit_button("📥 Registrar Entrada"):
                    if fardamento_id:
                        id_selecionado = int(fardamento_id.split(" - ")[0])
                        if registrar_movimentacao(id_selecionado, 'entrada', quantidade_entrada, responsavel_entrada, observacao_entrada):
                            st.rerun()
        
        with col2:
            st.subheader("➖ Saída de Estoque")
            with st.form("saida_estoque"):
                fardamento_id_saida = st.selectbox(
                    "Fardamento",
                    [f"{p['id']} - {p['nome']} ({p['tamanho']})" for p in st.session_state.produtos],
                    key="saida"
                )
                quantidade_saida = st.number_input("Quantidade", min_value=1, value=1, key="qtd_saida")
                responsavel_saida = st.text_input("Responsável", value=st.session_state.username, key="resp_saida")
                observacao_saida = st.text_input("Observação", placeholder
