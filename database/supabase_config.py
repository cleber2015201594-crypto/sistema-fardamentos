import streamlit as st
import pandas as pd
from datetime import datetime

# Tenta importar Supabase
try:
    import supabase
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    SUPABASE_AVAILABLE = False
    st.sidebar.warning(f"📦 Biblioteca Supabase não disponível: {e}")

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    if not SUPABASE_AVAILABLE:
        st.sidebar.error("❌ Supabase não disponível")
        return None
        
    try:
        # 🔥 USE SUAS CREDENCIAIS REAIS AQUI
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        
        if not url or not key:
            st.sidebar.error("❌ Credenciais do Supabase não configuradas")
            return None
        
        supabase_client = create_client(url, key)
        
        # Testar conexão simples
        try:
            result = supabase_client.table("fardamentos").select("*").limit(1).execute()
            st.sidebar.success("✅ Conectado ao Supabase!")
            return supabase_client
        except Exception as test_error:
            st.sidebar.warning(f"⚠️ Conexão testada: {test_error}")
            return supabase_client
            
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao conectar com Supabase: {str(e)}")
        return None

def criar_tabelas():
    """Tenta criar tabelas se não existirem"""
    supabase_client = init_supabase()
    if not supabase_client:
        return None
        
    try:
        # Verificar se tabela fardamentos existe
        result = supabase_client.table("fardamentos").select("*").limit(1).execute()
        st.sidebar.success("✅ Tabelas verificadas!")
        return supabase_client
    except Exception as e:
        st.sidebar.info("ℹ️ Tabelas serão criadas automaticamente")
        return supabase_client

# 🔧 FUNÇÕES PRINCIPAIS PARA FARDAMENTOS

def inserir_fardamento(nome, tamanho, quantidade, categoria="", responsavel="", observacoes=""):
    """Insere um novo fardamento no banco"""
    supabase_client = init_supabase()
    if not supabase_client:
        st.error("❌ Banco de dados não disponível")
        return None
        
    data = {
        "nome": nome,
        "tamanho": tamanho,
        "quantidade": quantidade,
        "categoria": categoria,
        "responsavel": responsavel,
        "observacoes": observacoes,
        "criado_em": datetime.now().isoformat()
    }
    
    try:
        result = supabase_client.table("fardamentos").insert(data).execute()
        if hasattr(result, 'data') and result.data:
            st.success(f"✅ Fardamento '{nome}' adicionado com sucesso!")
            return result.data[0]
        else:
            st.error("❌ Erro ao inserir fardamento: Resposta vazia")
            return None
    except Exception as e:
        st.error(f"❌ Erro ao inserir fardamento: {e}")
        return None

def buscar_fardamentos():
    """Busca todos os fardamentos"""
    supabase_client = init_supabase()
    if not supabase_client:
        return pd.DataFrame()
        
    try:
        result = supabase_client.table("fardamentos").select("*").order("id").execute()
        if hasattr(result, 'data') and result.data:
            df = pd.DataFrame(result.data)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar fardamentos: {e}")
        return pd.DataFrame()

def atualizar_fardamento(fardamento_id, dados_atualizados):
    """Atualiza um fardamento"""
    supabase_client = init_supabase()
    if not supabase_client:
        return False
        
    try:
        result = supabase_client.table("fardamentos").update(dados_atualizados).eq("id", fardamento_id).execute()
        if hasattr(result, 'data') and result.data:
            st.success("✅ Fardamento atualizado com sucesso!")
            return True
        else:
            return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar fardamento: {e}")
        return False

def excluir_fardamento(fardamento_id):
    """Exclui um fardamento"""
    supabase_client = init_supabase()
    if not supabase_client:
        return False
        
    try:
        result = supabase_client.table("fardamentos").delete().eq("id", fardamento_id).execute()
        if hasattr(result, 'data') and result.data:
            st.success("✅ Fardamento excluído com sucesso!")
            return True
        else:
            return False
    except Exception as e:
        st.error(f"❌ Erro ao excluir fardamento: {e}")
        return False

# 🔧 FUNÇÕES PARA PEDIDOS (usando session_state como fallback)

def inserir_pedido_supabase(dados_pedido):
    """Insere um novo pedido no banco"""
    supabase_client = init_supabase()
    if not supabase_client:
        # Fallback para session_state
        if 'pedidos' not in st.session_state:
            st.session_state.pedidos = []
        
        novo_id = len(st.session_state.pedidos) + 1
        dados_pedido['id'] = novo_id
        dados_pedido['criado_em'] = datetime.now().isoformat()
        
        st.session_state.pedidos.append(dados_pedido)
        st.success("✅ Pedido salvo localmente!")
        return dados_pedido
        
    try:
        result = supabase_client.table("pedidos").insert(dados_pedido).execute()
        if hasattr(result, 'data') and result.data:
            st.success("✅ Pedido cadastrado no Supabase!")
            return result.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"❌ Erro ao inserir pedido: {e}")
        return None

def buscar_pedidos_supabase():
    """Busca todos os pedidos"""
    supabase_client = init_supabase()
    if not supabase_client:
        # Fallback para session_state
        if 'pedidos' in st.session_state:
            return pd.DataFrame(st.session_state.pedidos)
        return pd.DataFrame()
        
    try:
        result = supabase_client.table("pedidos").select("*").order("id", desc=True).execute()
        if hasattr(result, 'data') and result.data:
            return pd.DataFrame(result.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar pedidos: {e}")
        return pd.DataFrame()

# 🔧 FUNÇÕES PARA CLIENTES

def inserir_cliente_supabase(dados_cliente):
    """Insere um novo cliente no banco"""
    supabase_client = init_supabase()
    if not supabase_client:
        # Fallback para session_state
        if 'clientes' not in st.session_state:
            st.session_state.clientes = []
        
        novo_id = len(st.session_state.clientes) + 1
        dados_cliente['id'] = novo_id
        dados_cliente['criado_em'] = datetime.now().isoformat()
        
        st.session_state.clientes.append(dados_cliente)
        st.success("✅ Cliente salvo localmente!")
        return dados_cliente
        
    try:
        result = supabase_client.table("clientes").insert(dados_cliente).execute()
        if hasattr(result, 'data') and result.data:
            st.success("✅ Cliente cadastrado no Supabase!")
            return result.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"❌ Erro ao inserir cliente: {e}")
        return None

def buscar_clientes_supabase():
    """Busca todos os clientes"""
    supabase_client = init_supabase()
    if not supabase_client:
        # Fallback para session_state
        if 'clientes' in st.session_state:
            return pd.DataFrame(st.session_state.clientes)
        return pd.DataFrame()
        
    try:
        result = supabase_client.table("clientes").select("*").order("id").execute()
        if hasattr(result, 'data') and result.data:
            return pd.DataFrame(result.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar clientes: {e}")
        return pd.DataFrame()

# 🔧 MIGRAÇÃO DE DADOS
def migrar_dados_para_supabase(dados_locais):
    """Migra dados locais para Supabase"""
    supabase_client = init_supabase()
    if not supabase_client:
        st.error("❌ Supabase não disponível para migração")
        return False
        
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        produtos_migrados = 0
        
        # Migrar produtos/fardamentos
        if 'produtos' in dados_locais and dados_locais['produtos']:
            for i, produto in enumerate(dados_locais['produtos']):
                data = {
                    "nome": str(produto.get('nome', '')),
                    "tamanho": str(produto.get('tamanho', '')),
                    "quantidade": int(produto.get('quantidade', 0)),
                    "categoria": str(produto.get('categoria', '')),
                    "responsavel": str(produto.get('responsavel', '')),
                    "observacoes": str(produto.get('observacoes', '')),
                    "criado_em": datetime.now().isoformat()
                }
                
                try:
                    supabase_client.table("fardamentos").insert(data).execute()
                    produtos_migrados += 1
                except Exception as insert_error:
                    st.warning(f"⚠️ Erro ao migrar produto {i+1}: {insert_error}")
                
                # Atualizar progresso
                progresso = (i + 1) / len(dados_locais['produtos'])
                progress_bar.progress(progresso)
                status_text.text(f"Migrando produtos... {i + 1}/{len(dados_locais['produtos'])}")
        
        progress_bar.empty()
        status_text.empty()
        
        if produtos_migrados > 0:
            st.success(f"✅ Migração concluída! {produtos_migrados} produtos migrados.")
        else:
            st.info("ℹ️ Nenhum produto migrado (possívelmente já existiam)")
            
        return produtos_migrados > 0
        
    except Exception as e:
        st.error(f"❌ Erro na migração: {e}")
        return False

# Função para verificar status
def verificar_status_supabase():
    """Verifica status da conexão com Supabase"""
    if not SUPABASE_AVAILABLE:
        return "❌ Biblioteca não instalada", False
    
    supabase_client = init_supabase()
    if supabase_client:
        try:
            # Teste simples
            result = supabase_client.table("fardamentos").select("count", count="exact").execute()
            return "✅ Conectado e funcionando", True
        except Exception as e:
            return f"⚠️ Conectado mas com erro: {str(e)}", True
    else:
        return "❌ Não conectado", False
