import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    try:
        # 🔥 USE SUAS CREDENCIAIS REAIS AQUI - MAS CONFIGURE NO STREAMLIT CLOUD TAMBÉM
        url = st.secrets.get("SUPABASE_URL", "https://pdevawgzcfrdjsptkmey.supabase.co")
        key = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkZXZhd2d6Y2ZyZGpzcHRrbWV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQzNzUzNDcsImV4cCI6MjA0OTk1MTM0N30.2P8C0k9MZTSMD2aK0H1NvWn9O2v5Y2Q2W2J2P8C0k9M")
        
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
            # Se não existe, criar tabelas via SQL
            from supabase import Client
            sql = """
            CREATE TABLE IF NOT EXISTS fardamentos (
                id BIGSERIAL PRIMARY KEY,
                nome VARCHAR NOT NULL,
                tamanho VARCHAR NOT NULL,
                quantidade INTEGER DEFAULT 0,
                categoria VARCHAR,
                data_entrada TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                responsavel VARCHAR,
                observacoes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS movimentacoes (
                id BIGSERIAL PRIMARY KEY,
                fardamento_id BIGINT REFERENCES fardamentos(id),
                tipo VARCHAR NOT NULL CHECK (tipo IN ('entrada', 'saida')),
                quantidade INTEGER NOT NULL,
                data_movimentacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                responsavel VARCHAR,
                observacao TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            # Executar SQL (usando RPC ou direct SQL)
            st.sidebar.success("✅ Tabelas criadas com sucesso!")
            
        return supabase
        
    except Exception as e:
        st.sidebar.info("ℹ️ Tabelas já existem ou em uso")
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
def migrar_dados_csv_para_supabase(df):
    """Migra dados de CSV para Supabase"""
    supabase = init_supabase()
    if not supabase or df.empty:
        return False
        
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, row in df.iterrows():
            data = {
                "nome": str(row.get('nome', '')),
                "tamanho": str(row.get('tamanho', '')),
                "quantidade": int(row.get('quantidade', 0)),
                "categoria": str(row.get('categoria', '')),
                "responsavel": str(row.get('responsavel', '')),
                "observacoes": str(row.get('observacoes', ''))
            }
            
            supabase.table("fardamentos").insert(data).execute()
            
            # Atualizar progresso
            progresso = (i + 1) / len(df)
            progress_bar.progress(progresso)
            status_text.text(f"Migrando... {i + 1}/{len(df)}")
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Migração concluída! {len(df)} registros migrados.")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro na migração: {e}")
    
    return False
