import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# =========================================
# 🗄️ SISTEMA AVANÇADO DE FARDAMENTOS
# =========================================

def sistema_hibrido():
    """Sistema local totalmente funcional"""
    return "👕 Sistema de Fardamentos - Premium", True

def salvar_fardamento(nome, tamanho, quantidade, categoria="", escola="", observacoes=""):
    """Salva um fardamento no sistema"""
    try:
        if 'produtos' not in st.session_state:
            st.session_state.produtos = []
            
        # Verificar se já existe fardamento igual
        for produto in st.session_state.produtos:
            if (produto['nome'] == nome and produto['tamanho'] == tamanho and 
                produto['categoria'] == categoria and produto['escola'] == escola):
                # Atualiza quantidade existente
                produto['quantidade'] += quantidade
                st.success(f"🔄 {nome} atualizado! Nova quantidade: {produto['quantidade']}")
                return True
            
        novo_fardamento = {
            'id': len(st.session_state.produtos) + 1,
            'nome': nome,
            'tamanho': tamanho,
            'quantidade': quantidade,
            'categoria': categoria,
            'escola': escola,
            'observacoes': observacoes,
            'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'ultima_atualizacao': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        st.session_state.produtos.append(novo_fardamento)
        st.success(f"✅ {nome} - {categoria} ({tamanho}) salvo com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {e}")
        return False

def buscar_fardamentos(filtro_escola=None, filtro_categoria=None):
    """Busca fardamentos com filtros"""
    if 'produtos' in st.session_state and st.session_state.produtos:
        df = pd.DataFrame(st.session_state.produtos)
        
        # Aplicar filtros
        if filtro_escola and filtro_escola != "Todas":
            df = df[df['escola'] == filtro_escola]
        if filtro_categoria and filtro_categoria != "Todas":
            df = df[df['categoria'] == filtro_categoria]
            
        return df
    return pd.DataFrame()

def atualizar_estoque(id_fardamento, nova_quantidade, motivo=""):
    """Atualiza estoque com histórico"""
    try:
        if 'produtos' in st.session_state:
            for i, produto in enumerate(st.session_state.produtos):
                if produto.get('id') == id_fardamento:
                    quantidade_antiga = produto['quantidade']
                    produto['quantidade'] = nova_quantidade
                    produto['ultima_atualizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    # Registrar no histórico
                    registrar_historico(
                        tipo="ESTOQUE",
                        fardamento_id=id_fardamento,
                        detalhes=f"Estoque alterado: {quantidade_antiga} → {nova_quantidade} - {motivo}"
                    )
                    
                    st.success(f"✅ Estoque atualizado: {quantidade_antiga} → {nova_quantidade}")
                    return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar: {e}")
        return False

def registrar_movimentacao(fardamento_id, tipo, quantidade, responsavel="", observacao=""):
    """Registra movimentação de entrada/saída"""
    try:
        if 'movimentacoes' not in st.session_state:
            st.session_state.movimentacoes = []
            
        movimentacao = {
            'id': len(st.session_state.movimentacoes) + 1,
            'fardamento_id': fardamento_id,
            'tipo': tipo,  # 'entrada' ou 'saida'
            'quantidade': quantidade,
            'responsavel': responsavel,
            'observacao': observacao,
            'data_movimentacao': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        st.session_state.movimentacoes.append(movimentacao)
        
        # Atualizar estoque automaticamente
        if tipo == 'entrada':
            fardamento = next((p for p in st.session_state.produtos if p['id'] == fardamento_id), None)
            if fardamento:
                fardamento['quantidade'] += quantidade
        elif tipo == 'saida':
            fardamento = next((p for p in st.session_state.produtos if p['id'] == fardamento_id), None)
            if fardamento:
                fardamento['quantidade'] = max(0, fardamento['quantidade'] - quantidade)
        
        st.success(f"✅ Movimentação de {tipo} registrada!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao registrar movimentação: {e}")
        return False

def buscar_movimentacoes(fardamento_id=None):
    """Busca movimentações"""
    if 'movimentacoes' in st.session_state and st.session_state.movimentacoes:
        df = pd.DataFrame(st.session_state.movimentacoes)
        if fardamento_id:
            df = df[df['fardamento_id'] == fardamento_id]
        return df
    return pd.DataFrame()

def registrar_historico(tipo, fardamento_id=None, detalhes=""):
    """Registra histórico de ações"""
    try:
        if 'historico' not in st.session_state:
            st.session_state.historico = []
            
        historico = {
            'id': len(st.session_state.historico) + 1,
            'tipo': tipo,
            'fardamento_id': fardamento_id,
            'detalhes': detalhes,
            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'usuario': st.session_state.get('username', 'Sistema')
        }
        
        st.session_state.historico.append(historico)
        return True
        
    except Exception:
        return False

def buscar_historico(limite=50):
    """Busca histórico do sistema"""
    if 'historico' in st.session_state and st.session_state.historico:
        df = pd.DataFrame(st.session_state.historico)
        return df.sort_values('data', ascending=False).head(limite)
    return pd.DataFrame()

# Funções para pedidos melhoradas
def salvar_pedido(dados_pedido):
    """Salva um pedido com validações"""
    try:
        if 'pedidos' not in st.session_state:
            st.session_state.pedidos = []
            
        # Validar estoque antes de salvar
        for item in dados_pedido.get('itens', []):
            fardamento = next((p for p in st.session_state.produtos 
                             if p['nome'] == item['nome'] and p['tamanho'] == item['tamanho']), None)
            
            if not fardamento:
                st.warning(f"⚠️ {item['nome']} ({item['tamanho']}) não encontrado em estoque")
                return False
                
            if fardamento['quantidade'] < item['quantidade']:
                st.error(f"❌ Estoque insuficiente: {item['nome']} ({item['tamanho']}) - Disponível: {fardamento['quantidade']}")
                return False
        
        dados_pedido['id'] = len(st.session_state.pedidos) + 1
        dados_pedido['criado_em'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        dados_pedido['numero_pedido'] = f"PED{datetime.now().strftime('%Y%m%d')}{len(st.session_state.pedidos) + 1:03d}"
        
        st.session_state.pedidos.append(dados_pedido)
        
        # Registrar no histórico
        registrar_historico(
            tipo="PEDIDO",
            detalhes=f"Novo pedido: {dados_pedido['cliente']} - {len(dados_pedido['itens'])} itens"
        )
        
        st.success(f"✅ Pedido {dados_pedido['numero_pedido']} salvo com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar pedido: {e}")
        return False

def buscar_pedidos(filtro_status=None, filtro_escola=None):
    """Busca pedidos com filtros"""
    if 'pedidos' in st.session_state and st.session_state.pedidos:
        df = pd.DataFrame(st.session_state.pedidos)
        
        if filtro_status and filtro_status != "Todos":
            df = df[df['status'] == filtro_status]
        if filtro_escola and filtro_escola != "Todas":
            df = df[df['escola'] == filtro_escola]
            
        return df
    return pd.DataFrame()

def atualizar_status_pedido(pedido_id, novo_status):
    """Atualiza status do pedido"""
    try:
        if 'pedidos' in st.session_state:
            for i, pedido in enumerate(st.session_state.pedidos):
                if pedido.get('id') == pedido_id:
                    status_antigo = pedido['status']
                    pedido['status'] = novo_status
                    
                    registrar_historico(
                        tipo="PEDIDO_STATUS",
                        detalhes=f"Pedido {pedido_id}: {status_antigo} → {novo_status}"
                    )
                    
                    st.success(f"✅ Status atualizado: {status_antigo} → {novo_status}")
                    return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {e}")
        return False

# Funções para clientes
def salvar_cliente(dados_cliente):
    """Salva um cliente"""
    try:
        if 'clientes' not in st.session_state:
            st.session_state.clientes = []
            
        dados_cliente['id'] = len(st.session_state.clientes) + 1
        dados_cliente['criado_em'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        st.session_state.clientes.append(dados_cliente)
        st.success("✅ Cliente salvo com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar cliente: {e}")
        return False

def buscar_clientes(filtro_escola=None):
    """Busca clientes com filtros"""
    if 'clientes' in st.session_state and st.session_state.clientes:
        df = pd.DataFrame(st.session_state.clientes)
        
        if filtro_escola and filtro_escola != "Todas":
            df = df[df['escola'] == filtro_escola]
            
        return df
    return pd.DataFrame()

# Funções de relatórios avançados
def gerar_relatorio_estoque():
    """Gera relatório completo de estoque"""
    if 'produtos' not in st.session_state or not st.session_state.produtos:
        return pd.DataFrame()
    
    df = pd.DataFrame(st.session_state.produtos)
    
    # Adicionar categorias de alerta
    def classificar_estoque(quantidade):
        if quantidade == 0:
            return "ESGOTADO"
        elif quantidade < 5:
            return "BAIXO"
        elif quantidade < 10:
            return "MEDIO"
        else:
            return "NORMAL"
    
    df['status_estoque'] = df['quantidade'].apply(classificar_estoque)
    return df

def gerar_estatisticas():
    """Gera estatísticas do sistema"""
    stats = {
        'total_fardamentos': len(st.session_state.get('produtos', [])),
        'total_pedidos': len(st.session_state.get('pedidos', [])),
        'total_clientes': len(st.session_state.get('clientes', [])),
        'estoque_total': sum(p.get('quantidade', 0) for p in st.session_state.get('produtos', [])),
        'pedidos_pendentes': len([p for p in st.session_state.get('pedidos', []) if p.get('status') == 'Pendente']),
        'alertas_estoque': len([p for p in st.session_state.get('produtos', []) if p.get('quantidade', 0) < 5])
    }
    return stats

def criar_tabelas_iniciais():
    """Inicializa estruturas se necessário"""
    if 'movimentacoes' not in st.session_state:
        st.session_state.movimentacoes = []
    if 'historico' not in st.session_state:
        st.session_state.historico = []
    return True
