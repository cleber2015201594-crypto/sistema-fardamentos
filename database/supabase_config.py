import streamlit as st
import pandas as pd
from datetime import datetime

# Tenta importar Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.sidebar.warning("📦 Biblioteca Supabase não instalada")

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    if not SUPABASE_AVAILABLE:
        return None
        
    try:
        # 🔥 USE SUAS CREDENCIAIS REAIS AQUI
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        
        supabase = create_client(url, key)
        
        # Testar conexão
        test_result = supabase.table("fardamentos").select("*").limit(1).execute()
        st.sidebar.success("✅ Conectado ao Supabase!")
        return supabase
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao conectar com Supabase: {e}")
        st.sidebar.info("Verifique as credenciais no Streamlit Cloud")
        return None

def criar_tabelas():
    """Cria as tabelas necessárias no Supabase"""
    supabase = init_supabase()
    if not supabase:
        return None
        
    try:
        # Verificar se tabela já existe
        result = supabase.table("fardamentos").select("*").limit(1).execute()
        
        if hasattr(result, 'error') and result.error:
            st.sidebar.info("📋 Criando tabelas...")
        else:
            st.sidebar.success("✅ Tabelas verificadas!")
            
        return supabase
        
    except Exception as e:
        st.sidebar.info("ℹ️ Tabelas em uso")
        return supabase

# 🔧 FUNÇÕES PRINCIPAIS PARA FARDAMENTOS

def inserir_fardamento(nome, tamanho, quantidade, categoria="", responsavel="", observacoes=""):
    """Insere um novo fardamento no banco"""
    supabase = init_supabase()
    if not supabase:
        return None
        
    data = {
        "nome": nome,
        "tamanho": tamanho,
        "quantidade": quantidade,
        "categoria": categoria,
        "responsavel": responsavel,
        "observacoes": observacoes
    }
    
    try:
        result = supabase.table("fardamentos").insert(data).execute()
        if result.data:
            st.success(f"✅ Fardamento '{nome}' adicionado com sucesso!")
            return result.data[0]
    except Exception as e:
        st.error(f"❌ Erro ao inserir fardamento: {e}")
    return None

def buscar_fardamentos():
    """Busca todos os fardamentos"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        result = supabase.table("fardamentos").select("*").order("id").execute()
        if result.data:
            df = pd.DataFrame(result.data)
            return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar fardamentos: {e}")
    
    return pd.DataFrame()

def atualizar_fardamento(fardamento_id, dados_atualizados):
    """Atualiza um fardamento"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        result = supabase.table("fardamentos").update(dados_atualizados).eq("id", fardamento_id).execute()
        if result.data:
            st.success("✅ Fardamento atualizado com sucesso!")
            return True
    except Exception as e:
        st.error(f"❌ Erro ao atualizar fardamento: {e}")
    
    return False

def excluir_fardamento(fardamento_id):
    """Exclui um fardamento"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        result = supabase.table("fardamentos").delete().eq("id", fardamento_id).execute()
        if result.data:
            st.success("✅ Fardamento excluído com sucesso!")
            return True
    except Exception as e:
        st.error(f"❌ Erro ao excluir fardamento: {e}")
    
    return False

# 🔧 FUNÇÕES PARA PEDIDOS

def inserir_pedido(dados_pedido):
    """Insere um novo pedido no banco"""
    supabase = init_supabase()
    if not supabase:
        return None
        
    try:
        result = supabase.table("pedidos").insert(dados_pedido).execute()
        if result.data:
            st.success("✅ Pedido cadastrado com sucesso!")
            return result.data[0]
    except Exception as e:
        st.error(f"❌ Erro ao inserir pedido: {e}")
    return None

def buscar_pedidos():
    """Busca todos os pedidos"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        result = supabase.table("pedidos").select("*").order("id", desc=True).execute()
        if result.data:
            df = pd.DataFrame(result.data)
            return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar pedidos: {e}")
    
    return pd.DataFrame()

# 🔧 FUNÇÕES PARA CLIENTES

def inserir_cliente(dados_cliente):
    """Insere um novo cliente no banco"""
    supabase = init_supabase()
    if not supabase:
        return None
        
    try:
        result = supabase.table("clientes").insert(dados_cliente).execute()
        if result.data:
            st.success("✅ Cliente cadastrado com sucesso!")
            return result.data[0]
    except Exception as e:
        st.error(f"❌ Erro ao inserir cliente: {e}")
    return None

def buscar_clientes():
    """Busca todos os clientes"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        result = supabase.table("clientes").select("*").order("id").execute()
        if result.data:
            df = pd.DataFrame(result.data)
            return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar clientes: {e}")
    
    return pd.DataFrame()

# 🔧 FUNÇÕES PARA MOVIMENTAÇÕES

def registrar_movimentacao(fardamento_id, tipo, quantidade, responsavel="", observacao=""):
    """Registra uma movimentação (entrada/saída)"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    data = {
        "fardamento_id": fardamento_id,
        "tipo": tipo,
        "quantidade": quantidade,
        "responsavel": responsavel,
        "observacao": observacao
    }
    
    try:
        # Registrar movimentação
        result = supabase.table("movimentacoes").insert(data).execute()
        
        # Atualizar estoque do fardamento
        fardamento = supabase.table("fardamentos").select("quantidade").eq("id", fardamento_id).execute()
        if fardamento.data:
            estoque_atual = fardamento.data[0]['quantidade']
            
            if tipo == 'entrada':
                novo_estoque = estoque_atual + quantidade
            else:  # saída
                novo_estoque = estoque_atual - quantidade
                if novo_estoque < 0:
                    st.warning("⚠️ Estoque ficará negativo!")
                    return False
            
            supabase.table("fardamentos").update({"quantidade": novo_estoque}).eq("id", fardamento_id).execute()
            
        st.success(f"✅ Movimentação de {tipo} registrada!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao registrar movimentação: {e}")
    
    return False

def buscar_movimentacoes(fardamento_id=None):
    """Busca movimentações"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        if fardamento_id:
            result = supabase.table("movimentacoes").select("*").eq("fardamento_id", fardamento_id).order("data_movimentacao", desc=True).execute()
        else:
            result = supabase.table("movimentacoes").select("*, fardamentos(nome, tamanho)").order("data_movimentacao", desc=True).execute()
        
        if result.data:
            return pd.DataFrame(result.data)
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar movimentações: {e}")
    
    return pd.DataFrame()

# 🔧 MIGRAÇÃO DE DADOS
def migrar_dados_para_supabase(dados_locais):
    """Migra dados locais para Supabase"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Migrar produtos/fardamentos
        if 'produtos' in dados_locais and dados_locais['produtos']:
            produtos_migrados = 0
            for i, produto in enumerate(dados_locais['produtos']):
                data = {
                    "nome": str(produto.get('nome', '')),
                    "tamanho": str(produto.get('tamanho', '')),
                    "quantidade": int(produto.get('quantidade', 0)),
                    "categoria": str(produto.get('categoria', '')),
                    "responsavel": str(produto.get('responsavel', '')),
                    "observacoes": str(produto.get('observacoes', ''))
                }
                
                supabase.table("fardamentos").insert(data).execute()
                produtos_migrados += 1
                
                # Atualizar progresso
                progresso = (i + 1) / len(dados_locais['produtos'])
                progress_bar.progress(progresso)
                status_text.text(f"Migrando produtos... {i + 1}/{len(dados_locais['produtos'])}")
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Migração concluída! {produtos_migrados} produtos migrados.")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro na migração: {e}")
    
    return False

# Função para verificar se Supabase está funcionando
def supabase_status():
    """Verifica status do Supabase"""
    if not SUPABASE_AVAILABLE:
        return "❌ Biblioteca não instalada"
    
    supabase = init_supabase()
    if supabase:
        try:
            result = supabase.table("fardamentos").select("*").limit(1).execute()
            return "✅ Conectado e funcionando"
        except Exception as e:
            return f"❌ Erro: {e}"
    else:
        return "❌ Não conectado"
