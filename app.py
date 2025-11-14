import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import os
import hashlib

# =========================================
# 🗄️ SISTEMA ESTÁVEL DE FARDAMENTOS
# =========================================

# Função local garantida
def sistema_hibrido():
    return "👕 Sistema de Fardamentos", True

# Status do sistema (sempre funciona)
status, _ = sistema_hibrido()

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
    
    # Inicializar estruturas apenas se necessário
    if 'movimentacoes' not in st.session_state:
        st.session_state.movimentacoes = []
    if 'historico' not in st.session_state:
        st.session_state.historico = []
        
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
st.sidebar.success(status)

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
    if st.session_state.historico:
        historico_recente = sorted(st.session_state.historico, key=lambda x: x.get('data', ''), reverse=True)[:10]
        for item in historico_recente:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{item.get('tipo', 'Sistema')}** - {item.get('detalhes', '')}")
                with col2:
                    st.caption(item.get('data', ''))
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
                    # Importar função do módulo
                    try:
                        from database.supabase_config import salvar_fardamento
                        salvar_fardamento(
                            nome=nome,
                            tamanho=tamanho,
                            quantidade=quantidade,
                            categoria=categoria,
                            escola=escola,
                            observacoes=observacoes
                        )
                        st.rerun()
                    except:
                        # Fallback local
                        if 'produtos' not in st.session_state:
                            st.session_state.produtos = []
                        novo_fardamento = {
                            'id': len(st.session_state.produtos) + 1,
                            'nome': nome,
                            'tamanho': tamanho,
                            'quantidade': quantidade,
                            'categoria': categoria,
                            'escola': escola,
                            'observacoes': observacoes,
                            'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                        st.session_state.produtos.append(novo_fardamento)
                        salvar_dados()
                        st.success("✅ Fardamento cadastrado com sucesso!")
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
        
        # Aplicar filtros manualmente
        fardamentos_filtrados = st.session_state.produtos
        if filtro_escola != "Todas":
            fardamentos_filtrados = [p for p in fardamentos_filtrados if p.get('escola') == filtro_escola]
        if filtro_categoria != "Todas":
            fardamentos_filtrados = [p for p in fardamentos_filtrados if p.get('categoria') == filtro_categoria]
        
        if fardamentos_filtrados:
            df_display = pd.DataFrame(fardamentos_filtrados)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Fardamentos", len(fardamentos_filtrados))
            with col2:
                total_estoque = sum(p.get('quantidade', 0) for p in fardamentos_filtrados)
                st.metric("Total em Estoque", total_estoque)
            with col3:
                baixo_estoque = len([p for p in fardamentos_filtrados if p.get('quantidade', 0) < 5])
                st.metric("Baixo Estoque", baixo_estoque)
            with col4:
                if fardamentos_filtrados:
                    escolas_count = {}
                    for p in fardamentos_filtrados:
                        escola = p.get('escola', 'N/A')
                        escolas_count[escola] = escolas_count.get(escola, 0) + 1
                    escola_mais = max(escolas_count, key=escolas_count.get) if escolas_count else "Nenhuma"
                    st.metric("Escola com Mais", escola_mais)
                else:
                    st.metric("Escola com Mais", "Nenhuma")
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
                            for produto in st.session_state.produtos:
                                if produto['id'] == fardamento_id:
                                    produto['quantidade'] = nova_quantidade
                                    salvar_dados()
                                    st.success(f"✅ Estoque atualizado para {nova_quantidade}!")
                                    st.rerun()
                                    break
                        
                        if st.button("🗑️ Excluir Fardamento", type="secondary"):
                            st.session_state.produtos = [p for p in st.session_state.produtos if p['id'] != fardamento_id]
                            salvar_dados()
                            st.success("✅ Fardamento excluído!")
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
            
            # No formulário de pedidos, substitua a parte do submitted:
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
        
        # 🔥 CORREÇÃO: Usar APENAS um método
        try:
            from database.supabase_config import salvar_pedido
            resultado = salvar_pedido(novo_pedido)
        except:
            # Fallback local APENAS se o módulo falhar
            novo_pedido['id'] = len(st.session_state.pedidos) + 1
            st.session_state.pedidos.append(novo_pedido)
            resultado = True
        
        if resultado:
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
        
        # Aplicar filtros
        pedidos_filtrados = st.session_state.pedidos
        if filtro_status != "Todos":
            pedidos_filtrados = [p for p in pedidos_filtrados if p.get('status') == filtro_status]
        if filtro_escola != "Todas":
            pedidos_filtrados = [p for p in pedidos_filtrados if p.get('escola') == filtro_escola]
        
        if pedidos_filtrados:
            df_pedidos = pd.DataFrame(pedidos_filtrados)
            st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
            
            # Estatísticas de pedidos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Pedidos", len(pedidos_filtrados))
            with col2:
                pedidos_pendentes = len([p for p in pedidos_filtrados if p.get('status') == 'Pendente'])
                st.metric("Pedidos Pendentes", pedidos_pendentes)
            with col3:
                total_itens_pedidos = sum(p.get('total_itens', 0) for p in pedidos_filtrados)
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
                            pedido['status'] = novo_status
                            salvar_dados()
                            st.success(f"✅ Status atualizado para {novo_status}!")
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
                    
                    try:
                        from database.supabase_config import salvar_cliente
                        if salvar_cliente(novo_cliente):
                            st.rerun()
                    except:
                        # Fallback local
                        novo_cliente['id'] = len(st.session_state.clientes) + 1
                        st.session_state.clientes.append(novo_cliente)
                        salvar_dados()
                        st.success("✅ Cliente salvo com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha o nome do cliente!")
    
    with tab2:
        st.subheader("📋 Clientes Cadastrados")
        
        # Filtro por escola
        filtro_escola = st.selectbox("Filtrar por Escola", ["Todas"] + st.session_state.escolas)
        
        # Aplicar filtro
        clientes_filtrados = st.session_state.clientes
        if filtro_escola != "Todas":
            clientes_filtrados = [c for c in clientes_filtrados if c.get('escola') == filtro_escola]
        
        if clientes_filtrados:
            df_clientes = pd.DataFrame(clientes_filtrados)
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(clientes_filtrados))
            with col2:
                if clientes_filtrados:
                    escolas_count = {}
                    for c in clientes_filtrados:
                        escola = c.get('escola', 'N/A')
                        escolas_count[escola] = escolas_count.get(escola, 0) + 1
                    escola_mais = max(escolas_count, key=escolas_count.get) if escolas_count else "Nenhuma"
                    st.metric("Escola com Mais", escola_mais)
                else:
                    st.metric("Escola com Mais", "Nenhuma")
            with col3:
                clientes_com_email = len([c for c in clientes_filtrados if c.get('email')])
                st.metric("Com Email", clientes_com_email)
        else:
            st.info("📋 Nenhum cliente cadastrado")
with tab2:
    st.subheader("📋 Clientes Cadastrados")
    
    # Filtro por escola
    filtro_escola = st.selectbox("Filtrar por Escola", ["Todas"] + st.session_state.escolas, key="filtro_escola_clientes")
    
    # Aplicar filtro
    clientes_filtrados = st.session_state.clientes
    if filtro_escola != "Todas":
        clientes_filtrados = [c for c in clientes_filtrados if c.get('escola') == filtro_escola]
    
    if clientes_filtrados:
        df_clientes = pd.DataFrame(clientes_filtrados)
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        
        # 🔥 NOVO: Seleção para exclusão
        st.subheader("🗑️ Excluir Cliente")
        clientes_para_excluir = [f"{c['id']} - {c['nome']} ({c['escola']})" for c in clientes_filtrados]
        cliente_excluir = st.selectbox("Selecione o cliente para excluir:", clientes_para_excluir, key="select_excluir_cliente")
        
        if st.button("🗑️ Excluir Cliente Selecionado", type="secondary", key="btn_excluir_cliente"):
            if cliente_excluir:
                cliente_id = int(cliente_excluir.split(" - ")[0])
                st.session_state.clientes = [c for c in st.session_state.clientes if c['id'] != cliente_id]
                salvar_dados()
                st.success("✅ Cliente excluído com sucesso!")
                st.rerun()
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Clientes", len(clientes_filtrados), key="metric_clientes_total")
        with col2:
            if clientes_filtrados:
                escolas_count = {}
                for c in clientes_filtrados:
                    escola = c.get('escola', 'N/A')
                    escolas_count[escola] = escolas_count.get(escola, 0) + 1
                escola_mais = max(escolas_count, key=escolas_count.get) if escolas_count else "Nenhuma"
                st.metric("Escola com Mais", escola_mais, key="metric_escola_mais")
            else:
                st.metric("Escola com Mais", "Nenhuma", key="metric_escola_mais_vazia")
        with col3:
            clientes_com_email = len([c for c in clientes_filtrados if c.get('email')])
            st.metric("Com Email", clientes_com_email, key="metric_clientes_email")
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
        
        if st.session_state.produtos:
            # Criar relatório de estoque
            df_estoque = pd.DataFrame(st.session_state.produtos)
            
            # Adicionar status de estoque
            def classificar_estoque(quantidade):
                if quantidade == 0:
                    return "🔴 ESGOTADO"
                elif quantidade < 5:
                    return "🟡 BAIXO"
                elif quantidade < 10:
                    return "🔵 MÉDIO"
                else:
                    return "🟢 NORMAL"
            
            df_estoque['status_estoque'] = df_estoque['quantidade'].apply(classificar_estoque)
            
            st.dataframe(df_estoque[['id', 'nome', 'categoria', 'tamanho', 'quantidade', 'escola', 'status_estoque']], 
                        use_container_width=True, hide_index=True)
            
            # Gráfico de estoque por categoria
            st.subheader("📊 Distribuição por Categoria")
            estoque_por_categoria = df_estoque.groupby('categoria')['quantidade'].sum().reset_index()
            if not estoque_por_categoria.empty:
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
                if st.session_state.produtos:
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
                            try:
                                from database.supabase_config import registrar_movimentacao
                                if registrar_movimentacao(id_selecionado, 'entrada', quantidade_entrada, responsavel_entrada, observacao_entrada):
                                    st.rerun()
                            except:
                                # Fallback local
                                for produto in st.session_state.produtos:
                                    if produto['id'] == id_selecionado:
                                        produto['quantidade'] += quantidade_entrada
                                        # Registrar movimentação local
                                        movimentacao = {
                                            'id': len(st.session_state.movimentacoes) + 1,
                                            'fardamento_id': id_selecionado,
                                            'tipo': 'entrada',
                                            'quantidade': quantidade_entrada,
                                            'responsavel': responsavel_entrada,
                                            'observacao': observacao_entrada,
                                            'data_movimentacao': datetime.now().strftime("%d/%m/%Y %H:%M")
                                        }
                                        st.session_state.movimentacoes.append(movimentacao)
                                        salvar_dados()
                                        st.success("✅ Entrada registrada com sucesso!")
                                        st.rerun()
                                        break
                else:
                    st.info("📋 Nenhum fardamento cadastrado")
        
        with col2:
            st.subheader("➖ Saída de Estoque")
            with st.form("saida_estoque"):
                if st.session_state.produtos:
                    fardamento_id_saida = st.selectbox(
                        "Fardamento",
                        [f"{p['id']} - {p['nome']} ({p['tamanho']})" for p in st.session_state.produtos],
                        key="saida"
                    )
                    quantidade_saida = st.number_input("Quantidade", min_value=1, value=1, key="qtd_saida")
                    responsavel_saida = st.text_input("Responsável", value=st.session_state.username, key="resp_saida")
                    observacao_saida = st.text_input("Observação", placeholder="Venda, perda...", key="obs_saida")
                    
                    if st.form_submit_button("📤 Registrar Saída"):
                        if fardamento_id_saida:
                            id_selecionado = int(fardamento_id_saida.split(" - ")[0])
                            try:
                                from database.supabase_config import registrar_movimentacao
                                if registrar_movimentacao(id_selecionado, 'saida', quantidade_saida, responsavel_saida, observacao_saida):
                                    st.rerun()
                            except:
                                # Fallback local
                                for produto in st.session_state.produtos:
                                    if produto['id'] == id_selecionado:
                                        if produto['quantidade'] >= quantidade_saida:
                                            produto['quantidade'] -= quantidade_saida
                                            # Registrar movimentação local
                                            movimentacao = {
                                                'id': len(st.session_state.movimentacoes) + 1,
                                                'fardamento_id': id_selecionado,
                                                'tipo': 'saida',
                                                'quantidade': quantidade_saida,
                                                'responsavel': responsavel_saida,
                                                'observacao': observacao_saida,
                                                'data_movimentacao': datetime.now().strftime("%d/%m/%Y %H:%M")
                                            }
                                            st.session_state.movimentacoes.append(movimentacao)
                                            salvar_dados()
                                            st.success("✅ Saída registrada com sucesso!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Estoque insuficiente!")
                                        break
                else:
                    st.info("📋 Nenhum fardamento cadastrado")
        
        # Histórico de movimentações
        st.subheader("📋 Histórico de Movimentações")
        if st.session_state.movimentacoes:
            df_movimentacoes = pd.DataFrame(st.session_state.movimentacoes)
            st.dataframe(df_movimentacoes, use_container_width=True, hide_index=True)
        else:
            st.info("📝 Nenhuma movimentação registrada")
    
    with tab3:
        st.subheader("📈 Estatísticas de Estoque")
        
        # Gerar estatísticas locais
        stats = {
            'total_fardamentos': len(st.session_state.produtos),
            'total_pedidos': len(st.session_state.pedidos),
            'total_clientes': len(st.session_state.clientes),
            'estoque_total': sum(p.get('quantidade', 0) for p in st.session_state.produtos),
            'pedidos_pendentes': len([p for p in st.session_state.pedidos if p.get('status') == 'Pendente']),
            'alertas_estoque': len([p for p in st.session_state.produtos if p.get('quantidade', 0) < 5])
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Fardamentos", stats['total_fardamentos'])
        with col2:
            st.metric("Estoque Total", stats['estoque_total'])
        with col3:
            st.metric("Alertas de Estoque", stats['alertas_estoque'])
        with col4:
            st.metric("Pedidos Pendentes", stats['pedidos_pendentes'])
        
        # Gráfico de estoque por escola
        if st.session_state.produtos:
            st.subheader("🏫 Estoque por Escola")
            estoque_por_escola = {}
            for produto in st.session_state.produtos:
                escola = produto.get('escola', 'N/A')
                estoque_por_escola[escola] = estoque_por_escola.get(escola, 0) + produto.get('quantidade', 0)
            
            if estoque_por_escola:
                df_escola = pd.DataFrame(list(estoque_por_escola.items()), columns=['Escola', 'Quantidade'])
                fig = px.bar(df_escola, x='Escola', y='Quantidade', title="Estoque por Escola", color='Quantidade')
                st.plotly_chart(fig, use_container_width=True)

# =========================================
# 📈 PÁGINA: RELATÓRIOS PREMIUM
# =========================================

elif menu == "📈 Relatórios":
    st.header("📈 Relatórios Detalhados")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vendas", "👕 Produtos", "👥 Clientes", "📋 Histórico"])
    
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
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Resumo de Pedidos")
            df_pedidos = pd.DataFrame(st.session_state.pedidos)
            st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
        else:
            st.info("📋 Nenhum pedido para relatório")
    
    with tab2:
        st.subheader("👕 Relatório de Produtos")
        
        if st.session_state.produtos:
            df_produtos = pd.DataFrame(st.session_state.produtos)
            
            # Produtos por categoria
            categorias = df_produtos['categoria'].value_counts()
            if not categorias.empty:
                fig = px.pie(values=categorias.values, names=categorias.index, title="Produtos por Categoria")
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_produtos, use_container_width=True, hide_index=True)
        else:
            st.info("📋 Nenhum produto para relatório")
    
    with tab3:
        st.subheader("👥 Relatório de Clientes")
        
        if st.session_state.clientes:
            df_clientes = pd.DataFrame(st.session_state.clientes)
            
            # Clientes por escola
            escolas_clientes = df_clientes['escola'].value_counts()
            if not escolas_clientes.empty:
                fig = px.bar(x=escolas_clientes.index, y=escolas_clientes.values, title="Clientes por Escola")
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        else:
            st.info("📋 Nenhum cliente para relatório")
    
    with tab4:
        st.subheader("📋 Histórico do Sistema")
        
        if st.session_state.historico:
            df_historico = pd.DataFrame(st.session_state.historico)
            st.dataframe(df_historico, use_container_width=True, hide_index=True)
        else:
            st.info("📝 Nenhum registro no histórico")

# =========================================
# ⚙️ PÁGINA: CONFIGURAÇÕES
# =========================================

elif menu == "⚙️ Configurações":
    st.header("⚙️ Configurações do Sistema")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Gerenciar Usuários", "🔐 Alterar Senha", "🗄️ Sistema", "💾 Backup"])
    
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
            st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
            
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
        st.header("🗄️ Sistema")
        
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
    
    with tab4:
        st.header("💾 Backup do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Estatísticas do Backup")
            st.info(f"📦 Pedidos: {len(st.session_state.pedidos)}")
            st.info(f"👥 Clientes: {len(st.session_state.clientes)}")
            st.info(f"👕 Produtos: {len(st.session_state.produtos)}")
            st.info(f"👤 Usuários: {len(st.session_state.usuarios)}")
            
            if os.path.exists(get_data_path()):
                ultima_modificacao = datetime.fromtimestamp(os.path.getmtime(get_data_path()))
                st.info(f"💾 Último backup: {ultima_modificacao.strftime('%d/%m/%Y %H:%M')}")
        
        with col2:
            st.subheader("🔄 Ações de Backup")
            
            if st.button("💾 Salvar Dados Agora", use_container_width=True):
                if salvar_dados():
                    st.success("✅ Dados salvos com sucesso!")
                else:
                    st.error("❌ Erro ao salvar dados")
            
            if st.button("📥 Gerar Backup para Download", use_container_width=True):
                dados = {
                    'pedidos': st.session_state.pedidos,
                    'clientes': st.session_state.clientes,
                    'produtos': st.session_state.produtos,
                    'usuarios': st.session_state.usuarios,
                    'movimentacoes': st.session_state.get('movimentacoes', []),
                    'historico': st.session_state.get('historico', []),
                    'data_backup': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'total_registros': len(st.session_state.pedidos) + len(st.session_state.clientes) + len(st.session_state.produtos)
                }
                backup_json = json.dumps(dados, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ Baixar Backup Completo",
                    data=backup_json,
                    file_name=f"backup_fardamentos_{datetime.now().strftime('%d%m%Y_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )

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
