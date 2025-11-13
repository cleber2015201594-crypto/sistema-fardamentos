import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================
# 🗄️ SISTEMA LOCAL SIMPLES (SEM SUPABASE)
# =========================================

def sistema_hibrido():
    """Sempre retorna modo local"""
    return "📱 Modo Local Ativo", False

# Funções locais simples
def salvar_fardamento(nome, tamanho, quantidade, categoria="", responsavel="", observacoes=""):
    """Salva um fardamento localmente"""
    try:
        if 'produtos' not in st.session_state:
            st.session_state.produtos = []
            
        novo_fardamento = {
            'id': len(st.session_state.produtos) + 1,
            'nome': nome,
            'tamanho': tamanho,
            'quantidade': quantidade,
            'categoria': categoria,
            'responsavel': responsavel,
            'observacoes': observacoes,
            'criado_em': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        st.session_state.produtos.append(novo_fardamento)
        st.success(f"✅ {nome} salvo localmente!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
        return False

def buscar_fardamentos():
    """Busca todos os fardamentos localmente"""
    if 'produtos' in st.session_state and st.session_state.produtos:
        return pd.DataFrame(st.session_state.produtos)
    return pd.DataFrame()

def atualizar_fardamento(id_fardamento, novos_dados):
    """Atualiza um fardamento localmente"""
    try:
        if 'produtos' in st.session_state:
            for i, produto in enumerate(st.session_state.produtos):
                if produto.get('id') == id_fardamento:
                    st.session_state.produtos[i].update(novos_dados)
                    st.success("✅ Fardamento atualizado!")
                    return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar: {e}")
        return False

def excluir_fardamento(id_fardamento):
    """Exclui um fardamento localmente"""
    try:
        if 'produtos' in st.session_state:
            st.session_state.produtos = [p for p in st.session_state.produtos if p.get('id') != id_fardamento]
            st.success("✅ Fardamento excluído!")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao excluir: {e}")
        return False

# Funções para pedidos
def salvar_pedido(dados_pedido):
    """Salva um pedido localmente"""
    try:
        if 'pedidos' not in st.session_state:
            st.session_state.pedidos = []
            
        dados_pedido['id'] = len(st.session_state.pedidos) + 1
        dados_pedido['criado_em'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        st.session_state.pedidos.append(dados_pedido)
        st.success("✅ Pedido salvo localmente!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar pedido: {e}")
        return False

def buscar_pedidos():
    """Busca todos os pedidos localmente"""
    if 'pedidos' in st.session_state and st.session_state.pedidos:
        return pd.DataFrame(st.session_state.pedidos)
    return pd.DataFrame()

# Funções para clientes
def salvar_cliente(dados_cliente):
    """Salva um cliente localmente"""
    try:
        if 'clientes' not in st.session_state:
            st.session_state.clientes = []
            
        dados_cliente['id'] = len(st.session_state.clientes) + 1
        dados_cliente['criado_em'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        st.session_state.clientes.append(dados_cliente)
        st.success("✅ Cliente salvo localmente!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar cliente: {e}")
        return False

def buscar_clientes():
    """Busca todos os clientes localmente"""
    if 'clientes' in st.session_state and st.session_state.clientes:
        return pd.DataFrame(st.session_state.clientes)
    return pd.DataFrame()

# Função vazia para compatibilidade
def criar_tabelas_iniciais():
    """Não faz nada no modo local"""
    pass
