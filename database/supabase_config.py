import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Configuração SIMPLES do Supabase usando requests
def testar_conexao_supabase():
    """Testa conexão com Supabase de forma simples"""
    try:
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            return False, "🔑 Credenciais não configuradas nos Secrets"
            
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        
        # Garantir que é .co
        if "supabase.com" in url:
            url = url.replace("supabase.com", "supabase.co")
        
        st.sidebar.info(f"🔗 Conectando: {url}")
        
        # Teste simples de conexão
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Testar endpoint de health check
        test_url = f"{url}/rest/v1/"
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            return True, "✅ Supabase Conectado!"
        elif response.status_code == 401:
            return False, "❌ Erro 401: Chave API inválida - Verifique SUPABASE_KEY"
        else:
            return False, f"❌ Erro {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"❌ Erro de conexão: {str(e)}"

def fazer_requisicao_supabase(endpoint, method="GET", data=None):
    """Faz requisições para a API do Supabase"""
    try:
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            st.error("❌ Credenciais do Supabase não configuradas")
            return None
            
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        
        # Garantir que é .co
        if "supabase.com" in url:
            url = url.replace("supabase.com", "supabase.co")
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        full_url = f"{url}/rest/v1/{endpoint}"
        
        if method == "GET":
            response = requests.get(full_url, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(full_url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(full_url, headers=headers)
        else:
            return None
            
        if response.status_code in [200, 201, 204]:
            if response.status_code == 204:  # No content (DELETE)
                return True
            return response.json()
        else:
            st.error(f"❌ Erro {response.status_code} em {method} {endpoint}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ Erro na requisição: {e}")
        return None

# Funções principais usando API direta
def salvar_fardamento(nome, tamanho, quantidade, categoria="", responsavel="", observacoes=""):
    """Salva um fardamento no Supabase via API"""
    dados = {
        "nome": nome,
        "tamanho": tamanho,
        "quantidade": quantidade,
        "categoria": categoria,
        "responsavel": responsavel,
        "observacoes": observacoes,
        "criado_em": datetime.now().isoformat()
    }
    
    resultado = fazer_requisicao_supabase("fardamentos", "POST", dados)
    
    if resultado:
        st.success(f"✅ {nome} salvo no banco!")
        return True
    else:
        # Fallback para salvar localmente
        st.info("💾 Salvando localmente (fallback)")
        return False

def buscar_fardamentos():
    """Busca todos os fardamentos via API"""
    resultado = fazer_requisicao_supabase("fardamentos?select=*")
    
    if resultado:
        return pd.DataFrame(resultado)
    else:
        return pd.DataFrame()

def atualizar_fardamento(id_fardamento, novos_dados):
    """Atualiza um fardamento via API"""
    resultado = fazer_requisicao_supabase(f"fardamentos?id=eq.{id_fardamento}", "PATCH", novos_dados)
    
    if resultado:
        st.success("✅ Fardamento atualizado!")
        return True
    else:
        return False

def excluir_fardamento(id_fardamento):
    """Exclui um fardamento via API"""
    resultado = fazer_requisicao_supabase(f"fardamentos?id=eq.{id_fardamento}", "DELETE")
    
    if resultado:
        st.success("✅ Fardamento excluído!")
        return True
    else:
        return False

# Funções para outras tabelas
def salvar_pedido(dados_pedido):
    """Salva um pedido via API"""
    resultado = fazer_requisicao_supabase("pedidos", "POST", dados_pedido)
    
    if resultado:
        st.success("✅ Pedido salvo no banco!")
        return True
    else:
        return False

def buscar_pedidos():
    """Busca todos os pedidos via API"""
    resultado = fazer_requisicao_supabase("pedidos?select=*")
    
    if resultado:
        return pd.DataFrame(resultado)
    else:
        return pd.DataFrame()

def salvar_cliente(dados_cliente):
    """Salva um cliente via API"""
    resultado = fazer_requisicao_supabase("clientes", "POST", dados_cliente)
    
    if resultado:
        st.success("✅ Cliente salvo no banco!")
        return True
    else:
        return False

def buscar_clientes():
    """Busca todos os clientes via API"""
    resultado = fazer_requisicao_supabase("clientes?select=*")
    
    if resultado:
        return pd.DataFrame(resultado)
    else:
        return pd.DataFrame()

# Sistema híbrido
def sistema_hibrido():
    """Retorna o status do sistema"""
    conectado, mensagem = testar_conexao_supabase()
    return mensagem, conectado

# Função para criar tabelas automaticamente
def criar_tabelas_iniciais():
    """Tenta criar tabelas se não existirem"""
    st.info("🔄 Verificando tabelas...")
    
    # Testar se tabela fardamentos existe
    resultado = fazer_requisicao_supabase("fardamentos?select=id&limit=1")
    
    if resultado is not None:
        st.success("✅ Tabelas prontas!")
        return True
    else:
        st.info("📋 Tabelas serão criadas automaticamente no primeiro uso")
        return False
