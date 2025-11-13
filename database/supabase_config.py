import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração simples do Supabase
def init_supabase():
    """Inicializa conexão com Supabase de forma simples"""
    try:
        # Verificar se secrets existem
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            st.sidebar.warning("🔑 Configure as credenciais do Supabase")
            return None
            
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        
        # Importação dentro da função para evitar erro de inicialização
        from supabase import create_client
        supabase_client = create_client(url, key)
        
        # Teste simples de conexão
        try:
            result = supabase_client.table("fardamentos").select("*").limit(1).execute()
            st.sidebar.success("🗄️ Supabase Conectado!")
            return supabase_client
        except Exception as e:
            # Se der erro, ainda retorna o cliente (tabelas serão criadas depois)
            st.sidebar.info("🔄 Conectado - Tabelas serão criadas automaticamente")
            return supabase_client
            
    except Exception as e:
        st.sidebar.error(f"❌ Erro na conexão: {str(e)}")
        return None

# Cache da conexão
@st.cache_resource
def get_supabase():
    return init_supabase()

# Funções principais simplificadas
def salvar_fardamento(nome, tamanho, quantidade, categoria="", responsavel="", observacoes=""):
    """Salva um fardamento no Supabase"""
    supabase = get_supabase()
    if not supabase:
        st.error("❌ Banco de dados não disponível")
        return False
        
    try:
        dados = {
            "nome": nome,
            "tamanho": tamanho,
            "quantidade": quantidade,
            "categoria": categoria,
            "responsavel": responsavel,
            "observacoes": observacoes,
            "criado_em": datetime.now().isoformat()
        }
        
        resultado = supabase.table("fardamentos").insert(dados).execute()
        
        if hasattr(resultado, 'data') and resultado.data:
            st.success(f"✅ {nome} salvo no banco!")
            return True
        else:
            st.error("❌ Erro ao salvar: Resposta vazia")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
        return False

def buscar_fardamentos():
    """Busca todos os fardamentos"""
    supabase = get_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        resultado = supabase.table("fardamentos").select("*").order("id").execute()
        if hasattr(resultado, 'data') and resultado.data:
            return pd.DataFrame(resultado.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar: {e}")
        return pd.DataFrame()

def atualizar_fardamento(id_fardamento, novos_dados):
    """Atualiza um fardamento"""
    supabase = get_supabase()
    if not supabase:
        return False
        
    try:
        resultado = supabase.table("fardamentos").update(novos_dados).eq("id", id_fardamento).execute()
        if hasattr(resultado, 'data') and resultado.data:
            st.success("✅ Fardamento atualizado!")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar: {e}")
        return False

def excluir_fardamento(id_fardamento):
    """Exclui um fardamento"""
    supabase = get_supabase()
    if not supabase:
        return False
        
    try:
        resultado = supabase.table("fardamentos").delete().eq("id", id_fardamento).execute()
        if hasattr(resultado, 'data') and resultado.data:
            st.success("✅ Fardamento excluído!")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao excluir: {e}")
        return False

# Funções para pedidos
def salvar_pedido(dados_pedido):
    """Salva um pedido no Supabase"""
    supabase = get_supabase()
    if not supabase:
        st.error("❌ Banco de dados não disponível")
        return False
        
    try:
        dados_pedido["criado_em"] = datetime.now().isoformat()
        resultado = supabase.table("pedidos").insert(dados_pedido).execute()
        
        if hasattr(resultado, 'data') and resultado.data:
            st.success("✅ Pedido salvo no banco!")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao salvar pedido: {e}")
        return False

def buscar_pedidos():
    """Busca todos os pedidos"""
    supabase = get_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        resultado = supabase.table("pedidos").select("*").order("id", desc=True).execute()
        if hasattr(resultado, 'data') and resultado.data:
            return pd.DataFrame(resultado.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar pedidos: {e}")
        return pd.DataFrame()

# Funções para clientes
def salvar_cliente(dados_cliente):
    """Salva um cliente no Supabase"""
    supabase = get_supabase()
    if not supabase:
        st.error("❌ Banco de dados não disponível")
        return False
        
    try:
        dados_cliente["criado_em"] = datetime.now().isoformat()
        resultado = supabase.table("clientes").insert(dados_cliente).execute()
        
        if hasattr(resultado, 'data') and resultado.data:
            st.success("✅ Cliente salvo no banco!")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao salvar cliente: {e}")
        return False

def buscar_clientes():
    """Busca todos os clientes"""
    supabase = get_supabase()
    if not supabase:
        return pd.DataFrame()
        
    try:
        resultado = supabase.table("clientes").select("*").order("id").execute()
        if hasattr(resultado, 'data') and resultado.data:
            return pd.DataFrame(resultado.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao buscar clientes: {e}")
        return pd.DataFrame()

# Sistema híbrido - usa Supabase se disponível, senão usa local
def sistema_hibrido():
    """Retorna o status do sistema"""
    supabase = get_supabase()
    if supabase:
        try:
            # Teste final
            supabase.table("fardamentos").select("count", count="exact").limit(1).execute()
            return "✅ Supabase Ativo", True
        except Exception as e:
            return f"⚠️ Supabase com problemas: {str(e)}", False
    else:
        return "📱 Modo Local", False
