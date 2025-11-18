import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os
import hashlib
import sqlite3

# =========================================
# 🔐 SISTEMA DE AUTENTICAÇÃO - SQLITE
# =========================================

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def get_connection():
    """Estabelece conexão com SQLite"""
    try:
        conn = sqlite3.connect('fardamentos.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"Erro de conexão com o banco: {str(e)}")
        return None

def init_db():
    """Inicializa o banco SQLite"""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Tabela de usuários
            cur.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nome_completo TEXT,
                    tipo TEXT DEFAULT 'vendedor',
                    ativo BOOLEAN DEFAULT 1,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de escolas
            cur.execute('''
                CREATE TABLE IF NOT EXISTS escolas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL
                )
            ''')
            
            # Tabela de clientes
            cur.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    email TEXT,
                    data_cadastro DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Tabela de produtos
            cur.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    tamanho TEXT,
                    cor TEXT,
                    preco REAL,
                    estoque INTEGER DEFAULT 0,
                    descricao TEXT,
                    escola_id INTEGER REFERENCES escolas(id),
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de pedidos (ATUALIZADA COM COLUNA TIPO)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER REFERENCES clientes(id),
                    escola_id INTEGER REFERENCES escolas(id),
                    status TEXT DEFAULT 'Pendente',
                    tipo TEXT DEFAULT 'venda',
                    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_entrega_prevista DATE,
                    data_entrega_real DATE,
                    forma_pagamento TEXT DEFAULT 'Dinheiro',
                    quantidade_total INTEGER,
                    valor_total REAL,
                    observacoes TEXT
                )
            ''')
            
            # Tabela de itens do pedido
            cur.execute('''
                CREATE TABLE IF NOT EXISTS pedido_itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
                    produto_id INTEGER REFERENCES produtos(id),
                    quantidade INTEGER,
                    preco_unitario REAL,
                    subtotal REAL
                )
            ''')
            
            # Inserir usuários padrão
            usuarios_padrao = [
                ('admin', make_hashes('Admin@2024!'), 'Administrador', 'admin'),
                ('vendedor', make_hashes('Vendas@123'), 'Vendedor', 'vendedor')
            ]
            
            for username, password_hash, nome, tipo in usuarios_padrao:
                try:
                    cur.execute('''
                        INSERT OR IGNORE INTO usuarios (username, password_hash, nome_completo, tipo) 
                        VALUES (?, ?, ?, ?)
                    ''', (username, password_hash, nome, tipo))
                except Exception as e:
                    pass
            
            # Inserir escolas padrão
            escolas_padrao = ['Municipal', 'Desperta', 'São Tadeu']
            for escola in escolas_padrao:
                try:
                    cur.execute('INSERT OR IGNORE INTO escolas (nome) VALUES (?)', (escola,))
                except Exception as e:
                    pass
            
            conn.commit()
            
        except Exception as e:
            st.error(f"Erro ao inicializar banco: {str(e)}")
        finally:
            conn.close()

def verificar_login(username, password):
    """Verifica credenciais no banco de dados"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão", None
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT password_hash, nome_completo, tipo 
            FROM usuarios 
            WHERE username = ? AND ativo = 1
        ''', (username,))
        
        resultado = cur.fetchone()
        
        if resultado and check_hashes(password, resultado[0]):
            return True, resultado[1], resultado[2]  # sucesso, nome, tipo
        else:
            return False, "Credenciais inválidas", None
            
    except Exception as e:
        return False, f"Erro: {str(e)}", None
    finally:
        conn.close()

def alterar_senha(username, senha_atual, nova_senha):
    """Altera a senha do usuário"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        # Verificar senha atual
        cur.execute('SELECT password_hash FROM usuarios WHERE username = ?', (username,))
        resultado = cur.fetchone()
        
        if not resultado or not check_hashes(senha_atual, resultado[0]):
            return False, "Senha atual incorreta"
        
        # Atualizar senha
        nova_senha_hash = make_hashes(nova_senha)
        cur.execute(
            'UPDATE usuarios SET password_hash = ? WHERE username = ?',
            (nova_senha_hash, username)
        )
        conn.commit()
        return True, "Senha alterada com sucesso!"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def listar_usuarios():
    """Lista todos os usuários (apenas para admin)"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT id, username, nome_completo, tipo, ativo, data_criacao 
            FROM usuarios 
            ORDER BY username
        ''')
        return cur.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return []
    finally:
        conn.close()

def criar_usuario(username, password, nome_completo, tipo):
    """Cria novo usuário (apenas para admin)"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        password_hash = make_hashes(password)
        
        cur.execute('''
            INSERT INTO usuarios (username, password_hash, nome_completo, tipo)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, nome_completo, tipo))
        
        conn.commit()
        return True, "Usuário criado com sucesso!"
        
    except sqlite3.IntegrityError:
        return False, "Username já existe"
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

# =========================================
# 🔐 SISTEMA DE LOGIN
# =========================================

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type='password')
    
    if st.sidebar.button("Entrar"):
        if username and password:
            sucesso, mensagem, tipo_usuario = verificar_login(username, password)
            if sucesso:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.nome_usuario = mensagem
                st.session_state.tipo_usuario = tipo_usuario
                st.sidebar.success(f"Bem-vindo, {mensagem}!")
                st.rerun()
            else:
                st.sidebar.error(mensagem)
        else:
            st.sidebar.error("Preencha todos os campos")

# Inicializar banco na primeira execução
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# =========================================
# 🚀 SISTEMA PRINCIPAL
# =========================================

st.set_page_config(
    page_title="Sistema de Fardamentos",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CONFIGURAÇÕES ESPECÍFICAS
tamanhos_infantil = ["2", "4", "6", "8", "10", "12"]
tamanhos_adulto = ["PP", "P", "M", "G", "GG"]
todos_tamanhos = tamanhos_infantil + tamanhos_adulto

categorias_produtos = ["Camisetas", "Calças/Shorts", "Agasalhos", "Acessórios", "Outros"]

# =========================================
# 🔧 FUNÇÕES DO BANCO DE DADOS - SQLITE
# =========================================

# FUNÇÕES PARA ESCOLAS
def listar_escolas():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM escolas ORDER BY nome")
        return cur.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar escolas: {e}")
        return []
    finally:
        conn.close()

def obter_escola_por_id(escola_id):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM escolas WHERE id = ?", (escola_id,))
        return cur.fetchone()
    except Exception as e:
        st.error(f"Erro ao obter escola: {e}")
        return None
    finally:
        conn.close()

# FUNÇÕES PARA CLIENTES
def adicionar_cliente(nome, telefone, email):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        data_cadastro = datetime.now().strftime("%Y-%m-%d")
        
        cur.execute(
            "INSERT INTO clientes (nome, telefone, email, data_cadastro) VALUES (?, ?, ?, ?)",
            (nome, telefone, email, data_cadastro)
        )
        
        conn.commit()
        return True, "Cliente cadastrado com sucesso!"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def listar_clientes():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM clientes ORDER BY nome')
        return cur.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar clientes: {e}")
        return []
    finally:
        conn.close()

def excluir_cliente(cliente_id):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        # Verificar se tem pedidos
        cur.execute("SELECT COUNT(*) FROM pedidos WHERE cliente_id = ?", (cliente_id,))
        if cur.fetchone()[0] > 0:
            return False, "Cliente possui pedidos e não pode ser excluído"
        
        cur.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        return True, "Cliente excluído com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

# FUNÇÕES PARA PRODUTOS
def verificar_produto_duplicado(nome, tamanho, cor, escola_id):
    """Verifica se já existe produto idêntico na mesma escola"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT COUNT(*) FROM produtos 
            WHERE nome = ? AND tamanho = ? AND cor = ? AND escola_id = ?
        ''', (nome, tamanho, cor, escola_id))
        
        return cur.fetchone()[0] > 0
    except Exception as e:
        st.error(f"Erro ao verificar produto: {e}")
        return False
    finally:
        conn.close()

def adicionar_produto(nome, categoria, tamanho, cor, preco, estoque, descricao, escola_id):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    # Verificar se produto já existe
    if verificar_produto_duplicado(nome, tamanho, cor, escola_id):
        escola_nome = obter_escola_por_id(escola_id)[1] if obter_escola_por_id(escola_id) else "a escola"
        return False, f"❌ Já existe um produto idêntico em {escola_nome}. Use o estoque existente."
    
    try:
        cur = conn.cursor()
        
        # CORREÇÃO: Garantir que o preço seja float
        preco_float = float(preco)
        
        cur.execute('''
            INSERT INTO produtos (nome, categoria, tamanho, cor, preco, estoque, descricao, escola_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, categoria, tamanho, cor, preco_float, estoque, descricao, escola_id))
        
        conn.commit()
        return True, "✅ Produto cadastrado com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def listar_produtos_por_escola(escola_id=None):
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        if escola_id:
            cur.execute('''
                SELECT p.*, e.nome as escola_nome 
                FROM produtos p 
                LEFT JOIN escolas e ON p.escola_id = e.id 
                WHERE p.escola_id = ?
                ORDER BY p.categoria, p.nome
            ''', (escola_id,))
        else:
            cur.execute('''
                SELECT p.*, e.nome as escola_nome 
                FROM produtos p 
                LEFT JOIN escolas e ON p.escola_id = e.id 
                ORDER BY e.nome, p.categoria, p.nome
            ''')
        return cur.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []
    finally:
        conn.close()

def atualizar_estoque(produto_id, nova_quantidade):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        cur.execute("UPDATE produtos SET estoque = ? WHERE id = ?", (nova_quantidade, produto_id))
        conn.commit()
        return True, "Estoque atualizado com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

# FUNÇÕES PARA PEDIDOS - SISTEMA COMPLETAMENTE CORRIGIDO
def adicionar_pedido_venda(cliente_id, escola_id, itens, data_entrega, forma_pagamento, observacoes):
    """Adiciona pedido como venda (baixa estoque imediatamente)"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        data_pedido = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        quantidade_total = sum(item['quantidade'] for item in itens)
        
        # CORREÇÃO: Calcular valor_total corretamente
        valor_total = 0
        for item in itens:
            # Garantir que preco_unitario e subtotal sejam floats
            preco_unitario = float(item['preco_unitario'])
            subtotal = preco_unitario * item['quantidade']
            valor_total += subtotal
        
        # Verificar estoque antes de processar
        for item in itens:
            cur.execute("SELECT estoque, nome FROM produtos WHERE id = ?", (item['produto_id'],))
            resultado = cur.fetchone()
            if resultado and resultado[0] < item['quantidade']:
                return False, f"❌ Estoque insuficiente para {resultado[1]}. Disponível: {resultado[0]}, Solicitado: {item['quantidade']}"
        
        cur.execute('''
            INSERT INTO pedidos (cliente_id, escola_id, data_entrega_prevista, forma_pagamento, 
            quantidade_total, valor_total, observacoes, status, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Concluído', 'venda')
        ''', (cliente_id, escola_id, data_entrega, forma_pagamento, quantidade_total, valor_total, observacoes))
        
        pedido_id = cur.lastrowid
        
        for item in itens:
            # CORREÇÃO: Garantir que os valores sejam float
            preco_unitario = float(item['preco_unitario'])
            subtotal = preco_unitario * item['quantidade']
            
            cur.execute('''
                INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (pedido_id, item['produto_id'], item['quantidade'], preco_unitario, subtotal))
            
            # Baixar estoque (apenas para vendas)
            cur.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", 
                       (item['quantidade'], item['produto_id']))
        
        conn.commit()
        return True, pedido_id
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def adicionar_pedido_producao(cliente_id, escola_id, itens, data_entrega, observacoes):
    """Adiciona pedido à produção (não mexe no estoque)"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        data_pedido = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        quantidade_total = sum(item['quantidade'] for item in itens)
        
        # CORREÇÃO: Calcular valor_total corretamente
        valor_total = 0
        for item in itens:
            preco_unitario = float(item['preco_unitario'])
            subtotal = preco_unitario * item['quantidade']
            valor_total += subtotal
        
        cur.execute('''
            INSERT INTO pedidos (cliente_id, escola_id, data_entrega_prevista, 
            quantidade_total, valor_total, observacoes, status, tipo)
            VALUES (?, ?, ?, ?, ?, ?, 'Em produção', 'producao')
        ''', (cliente_id, escola_id, data_entrega, quantidade_total, valor_total, observacoes))
        
        pedido_id = cur.lastrowid
        
        for item in itens:
            # CORREÇÃO: Garantir que os valores sejam float
            preco_unitario = float(item['preco_unitario'])
            subtotal = preco_unitario * item['quantidade']
            
            cur.execute('''
                INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (pedido_id, item['produto_id'], item['quantidade'], preco_unitario, subtotal))
        
        conn.commit()
        return True, pedido_id
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def finalizar_pedido_producao(pedido_id):
    """Finaliza pedido de produção e adiciona ao estoque - CORRIGIDA"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        # Buscar itens do pedido
        cur.execute('SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?', (pedido_id,))
        itens = cur.fetchall()
        
        # Atualizar estoque - CORREÇÃO: Adicionar ao estoque existente
        for item in itens:
            produto_id, quantidade = item[0], item[1]
            cur.execute("UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (quantidade, produto_id))
        
        # Marcar pedido como finalizado (Pronto para Entrega)
        cur.execute('''
            UPDATE pedidos 
            SET status = 'Pronto para entrega'
            WHERE id = ?
        ''', (pedido_id,))
        
        conn.commit()
        return True, "✅ Produção finalizada! Itens adicionados ao estoque e prontos para entrega."
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def entregar_pedido_producao(pedido_id):
    """Entrega pedido de produção (baixa estoque)"""
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        # Buscar itens do pedido
        cur.execute('SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?', (pedido_id,))
        itens = cur.fetchall()
        
        # Verificar estoque antes de entregar
        for item in itens:
            produto_id, quantidade = item[0], item[1]
            cur.execute("SELECT estoque, nome FROM produtos WHERE id = ?", (produto_id,))
            resultado = cur.fetchone()
            if resultado and resultado[0] < quantidade:
                return False, f"❌ Estoque insuficiente para entrega. Produto: {resultado[1]}, Disponível: {resultado[0]}, Necessário: {quantidade}"
        
        # Baixar estoque para entrega
        for item in itens:
            produto_id, quantidade = item[0], item[1]
            cur.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))
        
        # Marcar pedido como entregue
        cur.execute('''
            UPDATE pedidos 
            SET status = 'Entregue', data_entrega_real = ?
            WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d"), pedido_id))
        
        conn.commit()
        return True, "✅ Pedido entregue com sucesso! Estoque atualizado."
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def listar_pedidos_por_escola(escola_id=None, tipo=None):
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        query = '''
            SELECT p.*, c.nome as cliente_nome, e.nome as escola_nome
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            JOIN escolas e ON p.escola_id = e.id
        '''
        params = []
        
        conditions = []
        if escola_id:
            conditions.append("p.escola_id = ?")
            params.append(escola_id)
        if tipo:
            conditions.append("p.tipo = ?")
            params.append(tipo)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY p.data_pedido DESC"
        
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar pedidos: {e}")
        return []
    finally:
        conn.close()

def atualizar_status_pedido(pedido_id, novo_status):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        if novo_status == 'Entregue':
            data_entrega = datetime.now().strftime("%Y-%m-%d")
            cur.execute('''
                UPDATE pedidos 
                SET status = ?, data_entrega_real = ? 
                WHERE id = ?
            ''', (novo_status, data_entrega, pedido_id))
        else:
            cur.execute('''
                UPDATE pedidos 
                SET status = ? 
                WHERE id = ?
            ''', (novo_status, pedido_id))
        
        conn.commit()
        return True, "Status do pedido atualizado com sucesso!"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def excluir_pedido(pedido_id):
    conn = get_connection()
    if not conn:
        return False, "Erro de conexão"
    
    try:
        cur = conn.cursor()
        
        # Verificar tipo do pedido para restaurar estoque se necessário
        cur.execute('SELECT tipo, status FROM pedidos WHERE id = ?', (pedido_id,))
        resultado = cur.fetchone()
        if resultado:
            tipo_pedido, status = resultado[0], resultado[1]
            
            if tipo_pedido == 'venda':
                # Restaurar estoque para pedidos de venda
                cur.execute('SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?', (pedido_id,))
                itens = cur.fetchall()
                
                for item in itens:
                    produto_id, quantidade = item[0], item[1]
                    cur.execute("UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (quantidade, produto_id))
            
            elif tipo_pedido == 'producao' and status == 'Pronto para entrega':
                # Se era produção pronta para entrega, remover do estoque
                cur.execute('SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?', (pedido_id,))
                itens = cur.fetchall()
                
                for item in itens:
                    produto_id, quantidade = item[0], item[1]
                    cur.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))
        
        # Excluir pedido
        cur.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        
        conn.commit()
        return True, "Pedido excluído com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

# =========================================
# 📊 FUNÇÕES PARA RELATÓRIOS - SQLITE
# =========================================

def gerar_relatorio_vendas_por_escola(escola_id=None):
    """Gera relatório de vendas por período e escola"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cur = conn.cursor()
        
        if escola_id:
            cur.execute('''
                SELECT 
                    DATE(p.data_pedido) as data,
                    COUNT(*) as total_pedidos,
                    SUM(p.quantidade_total) as total_itens,
                    SUM(p.valor_total) as total_vendas
                FROM pedidos p
                WHERE p.escola_id = ? AND p.tipo = 'venda'
                GROUP BY DATE(p.data_pedido)
                ORDER BY data DESC
            ''', (escola_id,))
        else:
            cur.execute('''
                SELECT 
                    DATE(p.data_pedido) as data,
                    e.nome as escola,
                    COUNT(*) as total_pedidos,
                    SUM(p.quantidade_total) as total_itens,
                    SUM(p.valor_total) as total_vendas
                FROM pedidos p
                JOIN escolas e ON p.escola_id = e.id
                WHERE p.tipo = 'venda'
                GROUP BY DATE(p.data_pedido), e.nome
                ORDER BY data DESC
            ''')
            
        dados = cur.fetchall()
        
        if dados:
            if escola_id:
                df = pd.DataFrame(dados, columns=['Data', 'Total Pedidos', 'Total Itens', 'Total Vendas (R$)'])
            else:
                df = pd.DataFrame(dados, columns=['Data', 'Escola', 'Total Pedidos', 'Total Itens', 'Total Vendas (R$)'])
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def gerar_relatorio_produtos_por_escola(escola_id=None):
    """Gera relatório de produtos mais vendidos por escola"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cur = conn.cursor()
        
        if escola_id:
            cur.execute('''
                SELECT 
                    pr.nome as produto,
                    pr.categoria,
                    pr.tamanho,
                    pr.cor,
                    SUM(pi.quantidade) as total_vendido,
                    SUM(pi.subtotal) as total_faturado
                FROM pedido_itens pi
                JOIN produtos pr ON pi.produto_id = pr.id
                JOIN pedidos p ON pi.pedido_id = p.id
                WHERE p.escola_id = ? AND p.tipo = 'venda'
                GROUP BY pr.id, pr.nome, pr.categoria, pr.tamanho, pr.cor
                ORDER BY total_vendido DESC
            ''', (escola_id,))
        else:
            cur.execute('''
                SELECT 
                    pr.nome as produto,
                    pr.categoria,
                    pr.tamanho,
                    pr.cor,
                    e.nome as escola,
                    SUM(pi.quantidade) as total_vendido,
                    SUM(pi.subtotal) as total_faturado
                FROM pedido_itens pi
                JOIN produtos pr ON pi.produto_id = pr.id
                JOIN pedidos p ON pi.pedido_id = p.id
                JOIN escolas e ON p.escola_id = e.id
                WHERE p.tipo = 'venda'
                GROUP BY pr.id, pr.nome, pr.categoria, pr.tamanho, pr.cor, e.nome
                ORDER BY total_vendido DESC
            ''')
            
        dados = cur.fetchall()
        
        if dados:
            if escola_id:
                df = pd.DataFrame(dados, columns=['Produto', 'Categoria', 'Tamanho', 'Cor', 'Total Vendido', 'Total Faturado (R$)'])
            else:
                df = pd.DataFrame(dados, columns=['Produto', 'Categoria', 'Tamanho', 'Cor', 'Escola', 'Total Vendido', 'Total Faturado (R$)'])
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# =========================================
# 🎨 INTERFACE PRINCIPAL
# =========================================

# Sidebar - Informações do usuário
st.sidebar.markdown("---")
st.sidebar.write(f"👤 **Usuário:** {st.session_state.nome_usuario}")
st.sidebar.write(f"🎯 **Tipo:** {st.session_state.tipo_usuario}")

# Menu de gerenciamento de usuários (apenas para admin)
if st.session_state.tipo_usuario == 'admin':
    with st.sidebar.expander("👥 Gerenciar Usuários"):
        st.subheader("Novo Usuário")
        with st.form("novo_usuario"):
            novo_username = st.text_input("Username")
            nova_senha = st.text_input("Senha", type='password')
            nome_completo = st.text_input("Nome Completo")
            tipo = st.selectbox("Tipo", ["admin", "vendedor"])
            
            if st.form_submit_button("Criar Usuário"):
                if novo_username and nova_senha and nome_completo:
                    sucesso, msg = criar_usuario(novo_username, nova_senha, nome_completo, tipo)
                    if sucesso:
                        st.success(msg)
                    else:
                        st.error(msg)
        
        st.subheader("Usuários do Sistema")
        usuarios = listar_usuarios()
        if usuarios:
            for usuario in usuarios:
                status = "✅ Ativo" if usuario[4] == 1 else "❌ Inativo"
                st.write(f"**{usuario[1]}** - {usuario[2]} ({usuario[3]}) - {status}")

# Menu de alteração de senha
with st.sidebar.expander("🔐 Alterar Senha"):
    with st.form("alterar_senha"):
        senha_atual = st.text_input("Senha Atual", type='password')
        nova_senha1 = st.text_input("Nova Senha", type='password')
        nova_senha2 = st.text_input("Confirmar Nova Senha", type='password')
        
        if st.form_submit_button("Alterar Senha"):
            if senha_atual and nova_senha1 and nova_senha2:
                if nova_senha1 == nova_senha2:
                    sucesso, msg = alterar_senha(st.session_state.username, senha_atual, nova_senha1)
                    if sucesso:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("As novas senhas não coincidem")
            else:
                st.error("Preencha todos os campos")

# Botão de logout
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome_usuario = None
    st.session_state.tipo_usuario = None
    st.rerun()

# Menu principal - ATUALIZADO COM PRODUÇÃO
st.sidebar.title("👕 Sistema de Fardamentos")
menu_options = ["📊 Dashboard", "🛒 Vendas", "🏭 Produção", "👥 Clientes", "👕 Produtos", "📦 Estoque", "📈 Relatórios"]
menu = st.sidebar.radio("Navegação", menu_options)

# Header dinâmico
if menu == "📊 Dashboard":
    st.title("📊 Dashboard - Visão Geral")
elif menu == "🛒 Vendas":
    st.title("🛒 Gestão de Vendas") 
elif menu == "🏭 Produção":
    st.title("🏭 Controle de Produção")
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
elif menu == "👕 Produtos":
    st.title("👕 Gestão de Produtos")
elif menu == "📦 Estoque":
    st.title("📦 Controle de Estoque")
elif menu == "📈 Relatórios":
    st.title("📈 Relatórios Detalhados")

st.markdown("---")

# =========================================
# 📱 PÁGINAS DO SISTEMA
# =========================================

if menu == "📊 Dashboard":
    st.header("🎯 Métricas em Tempo Real")
    
    # Carregar dados
    escolas = listar_escolas()
    clientes = listar_clientes()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pedidos = 0
        for escola in escolas:
            pedidos = listar_pedidos_por_escola(escola[0])
            total_pedidos += len(pedidos)
        st.metric("Total de Pedidos", total_pedidos)
    
    with col2:
        pedidos_producao = 0
        for escola in escolas:
            pedidos = listar_pedidos_por_escola(escola[0], tipo='producao')
            pedidos_producao += len([p for p in pedidos if p[3] == 'Em produção'])
        st.metric("Pedidos em Produção", pedidos_producao)
    
    with col3:
        st.metric("Clientes Ativos", len(clientes))
    
    with col4:
        produtos_baixo_estoque = 0
        for escola in escolas:
            produtos = listar_produtos_por_escola(escola[0])
            produtos_baixo_estoque += len([p for p in produtos if p[6] < 5])
        st.metric("Alertas de Estoque", produtos_baixo_estoque, delta=-produtos_baixo_estoque)
    
    # Métricas por Escola
    st.header("🏫 Métricas por Escola")
    escolas_cols = st.columns(len(escolas))
    
    for idx, escola in enumerate(escolas):
        with escolas_cols[idx]:
            st.subheader(escola[1])
            
            # Pedidos da escola
            pedidos_escola = listar_pedidos_por_escola(escola[0])
            pedidos_producao_escola = len([p for p in pedidos_escola if p[3] == 'Em produção'])
            
            # Produtos da escola
            produtos_escola = listar_produtos_por_escola(escola[0])
            produtos_baixo_estoque_escola = len([p for p in produtos_escola if p[6] < 5])
            
            st.metric("Pedidos", len(pedidos_escola))
            st.metric("Em Produção", pedidos_producao_escola)
            st.metric("Produtos", len(produtos_escola))
            st.metric("Alerta Estoque", produtos_baixo_estoque_escola)
    
    # Ações Rápidas
    st.header("⚡ Ações Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛒 Nova Venda", use_container_width=True):
            st.session_state.menu = "🛒 Vendas"
            st.rerun()
    
    with col2:
        if st.button("🏭 Nova Produção", use_container_width=True):
            st.session_state.menu = "🏭 Produção"
            st.rerun()
    
    with col3:
        if st.button("👕 Cadastrar Produto", use_container_width=True):
            st.session_state.menu = "👕 Produtos"
            st.rerun()

elif menu == "👥 Clientes":
    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar Cliente", "📋 Listar Clientes", "🗑️ Excluir Cliente"])
    
    with tab1:
        st.header("➕ Novo Cliente")
        
        nome = st.text_input("👤 Nome completo*")
        telefone = st.text_input("📞 Telefone")
        email = st.text_input("📧 Email")
        
        if st.button("✅ Cadastrar Cliente", type="primary"):
            if nome:
                sucesso, msg = adicionar_cliente(nome, telefone, email)
                if sucesso:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
            else:
                st.error("❌ Nome é obrigatório!")
    
    with tab2:
        st.header("📋 Clientes Cadastrados")
        clientes = listar_clientes()
        
        if clientes:
            dados = []
            for cliente in clientes:
                dados.append({
                    'ID': cliente[0],
                    'Nome': cliente[1],
                    'Telefone': cliente[2] or 'N/A',
                    'Email': cliente[3] or 'N/A',
                    'Data Cadastro': cliente[4]
                })
            
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
        else:
            st.info("👥 Nenhum cliente cadastrado")
    
    with tab3:
        st.header("🗑️ Excluir Cliente")
        clientes = listar_clientes()
        
        if clientes:
            cliente_selecionado = st.selectbox(
                "Selecione o cliente para excluir:",
                [f"{c[1]} (ID: {c[0]})" for c in clientes]
            )
            
            if cliente_selecionado:
                cliente_id = int(cliente_selecionado.split("(ID: ")[1].replace(")", ""))
                
                st.warning("⚠️ Esta ação não pode ser desfeita!")
                if st.button("🗑️ Confirmar Exclusão", type="primary"):
                    sucesso, msg = excluir_cliente(cliente_id)
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("👥 Nenhum cliente cadastrado")

elif menu == "👕 Produtos":
    escolas = listar_escolas()
    
    if not escolas:
        st.error("❌ Nenhuma escola cadastrada. Configure as escolas primeiro.")
        st.stop()
    
    # Seleção da escola
    escola_selecionada_nome = st.selectbox(
        "🏫 Selecione a Escola:",
        [e[1] for e in escolas],
        key="produtos_escola"
    )
    
    escola_id = next(e[0] for e in escolas if e[1] == escola_selecionada_nome)
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Produto", "📋 Produtos da Escola"])
    
    with tab1:
        st.header(f"➕ Novo Produto - {escola_selecionada_nome}")
        
        with st.form("novo_produto", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("📝 Nome do produto*", placeholder="Ex: Camiseta Básica")
                categoria = st.selectbox("📂 Categoria*", categorias_produtos)
                tamanho = st.selectbox("📏 Tamanho*", todos_tamanhos)
                cor = st.text_input("🎨 Cor*", value="Branco", placeholder="Ex: Azul Marinho")
            
            with col2:
                # CORREÇÃO: Usar step 0.01 para garantir casas decimais
                preco = st.number_input("💰 Preço (R$)*", min_value=0.0, value=29.90, step=0.01, format="%.2f")
                estoque = st.number_input("📦 Estoque inicial*", min_value=0, value=10)
                descricao = st.text_area("📄 Descrição", placeholder="Detalhes do produto...")
            
            if st.form_submit_button("✅ Cadastrar Produto", type="primary"):
                if nome and cor:
                    sucesso, msg = adicionar_produto(nome, categoria, tamanho, cor, preco, estoque, descricao, escola_id)
                    if sucesso:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Campos obrigatórios: Nome e Cor")
    
    with tab2:
        st.header(f"📋 Produtos - {escola_selecionada_nome}")
        produtos = listar_produtos_por_escola(escola_id)
        
        if produtos:
            # Métricas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                total_produtos = len(produtos)
                st.metric("Total de Produtos", total_produtos)
            with col2:
                total_estoque = sum(p[6] for p in produtos)
                st.metric("Estoque Total", total_estoque)
            with col3:
                baixo_estoque = len([p for p in produtos if p[6] < 5])
                st.metric("Produtos com Estoque Baixo", baixo_estoque)
            
            # Tabela de produtos
            dados = []
            for produto in produtos:
                status_estoque = "✅" if produto[6] >= 5 else "⚠️" if produto[6] > 0 else "❌"
                
                dados.append({
                    'ID': produto[0],
                    'Produto': produto[1],
                    'Categoria': produto[2],
                    'Tamanho': produto[3],
                    'Cor': produto[4],
                    'Preço': f"R$ {produto[5]:.2f}",
                    'Estoque': f"{status_estoque} {produto[6]}",
                    'Descrição': produto[7] or 'N/A'
                })
            
            df = pd.DataFrame(dados)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Estatísticas por categoria
            st.subheader("📊 Estatísticas por Categoria")
            categorias_df = pd.DataFrame([(p[2], p[6]) for p in produtos], columns=['Categoria', 'Estoque'])
            resumo_categorias = categorias_df.groupby('Categoria').agg({
                'Estoque': ['count', 'sum']
            }).round(0)
            resumo_categorias.columns = ['Qtd Produtos', 'Total Estoque']
            st.dataframe(resumo_categorias, use_container_width=True)
            
        else:
            st.info(f"👕 Nenhum produto cadastrado para {escola_selecionada_nome}")

elif menu == "📦 Estoque":
    escolas = listar_escolas()
    
    if not escolas:
        st.error("❌ Nenhuma escola cadastrada. Configure as escolas primeiro.")
        st.stop()
    
    # Abas por escola
    tabs = st.tabs([f"🏫 {e[1]}" for e in escolas])
    
    for idx, escola in enumerate(escolas):
        with tabs[idx]:
            st.header(f"📦 Controle de Estoque - {escola[1]}")
            
            produtos = listar_produtos_por_escola(escola[0])
            
            if produtos:
                # Métricas da escola
                col1, col2, col3, col4 = st.columns(4)
                total_produtos = len(produtos)
                total_estoque = sum(p[6] for p in produtos)
                produtos_baixo_estoque = len([p for p in produtos if p[6] < 5])
                produtos_sem_estoque = len([p for p in produtos if p[6] == 0])
                
                with col1:
                    st.metric("Total Produtos", total_produtos)
                with col2:
                    st.metric("Estoque Total", total_estoque)
                with col3:
                    st.metric("Estoque Baixo", produtos_baixo_estoque)
                with col4:
                    st.metric("Sem Estoque", produtos_sem_estoque)
                
                # Tabela interativa de estoque
                st.subheader("📋 Ajuste de Estoque")
                
                for produto in produtos:
                    with st.expander(f"{produto[1]} - {produto[3]} - {produto[4]} (Estoque: {produto[6]})"):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Categoria:** {produto[2]}")
                            st.write(f"**Preço:** R$ {produto[5]:.2f}")
                            if produto[7]:
                                st.write(f"**Descrição:** {produto[7]}")
                        
                        with col2:
                            nova_quantidade = st.number_input(
                                "Nova quantidade",
                                min_value=0,
                                value=produto[6],
                                key=f"estoque_{produto[0]}_{idx}"
                            )
                        
                        with col3:
                            if st.button("💾 Atualizar", key=f"btn_{produto[0]}_{idx}"):
                                if nova_quantidade != produto[6]:
                                    sucesso, msg = atualizar_estoque(produto[0], nova_quantidade)
                                    if sucesso:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                else:
                                    st.info("Quantidade não foi alterada")
                
                # Alertas de estoque baixo
                produtos_alerta = [p for p in produtos if p[6] < 5]
                if produtos_alerta:
                    st.subheader("🚨 Alertas de Estoque Baixo")
                    for produto in produtos_alerta:
                        st.warning(f"**{produto[1]} - {produto[3]} - {produto[4]}**: Apenas {produto[6]} unidades em estoque")
            
            else:
                st.info(f"👕 Nenhum produto cadastrado para {escola[1]}")

elif menu == "🛒 Vendas":
    escolas = listar_escolas()
    
    if not escolas:
        st.error("❌ Nenhuma escola cadastrada. Configure as escolas primeiro.")
        st.stop()
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Nova Venda", "📋 Todas as Vendas", "🔄 Gerenciar Vendas", "📊 Por Escola"])
    
    with tab1:
        st.header("➕ Nova Venda")
        
        # Seleção da escola para o pedido
        escola_pedido_nome = st.selectbox(
            "🏫 Escola da Venda:",
            [e[1] for e in escolas],
            key="venda_escola"
        )
        escola_pedido_id = next(e[0] for e in escolas if e[1] == escola_pedido_nome)
        
        # Selecionar cliente
        clientes = listar_clientes()
        if not clientes:
            st.error("❌ Nenhum cliente cadastrado. Cadastre clientes primeiro.")
        else:
            cliente_selecionado = st.selectbox(
                "👤 Selecione o cliente:",
                [f"{c[1]} (ID: {c[0]})" for c in clientes]
            )
            
            if cliente_selecionado:
                cliente_id = int(cliente_selecionado.split("(ID: ")[1].replace(")", ""))
                
                # Produtos da escola selecionada
                produtos = listar_produtos_por_escola(escola_pedido_id)
                
                if produtos:
                    st.subheader(f"🛒 Produtos Disponíveis - {escola_pedido_nome}")
                    
                    # Interface para adicionar itens
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        produto_selecionado = st.selectbox(
                            "Produto:",
                            [f"{p[1]} - Tamanho: {p[3]} - Cor: {p[4]} - Estoque: {p[6]} - R$ {p[5]:.2f}" for p in produtos],
                            key="produto_venda"
                        )
                    with col2:
                        quantidade = st.number_input("Quantidade", min_value=1, value=1, key="qtd_venda")
                    with col3:
                        if st.button("➕ Adicionar Item", use_container_width=True):
                            if 'itens_venda' not in st.session_state:
                                st.session_state.itens_venda = []
                            
                            produto_id = next(p[0] for p in produtos if f"{p[1]} - Tamanho: {p[3]} - Cor: {p[4]} - Estoque: {p[6]} - R$ {p[5]:.2f}" == produto_selecionado)
                            produto = next(p for p in produtos if p[0] == produto_id)
                            
                            if quantidade > produto[6]:
                                st.error(f"❌ Quantidade indisponível em estoque! Disponível: {produto[6]}")
                            else:
                                # Verificar se produto já está no pedido
                                item_existente = next((i for i in st.session_state.itens_venda if i['produto_id'] == produto_id), None)
                                
                                if item_existente:
                                    item_existente['quantidade'] += quantidade
                                    item_existente['subtotal'] = item_existente['quantidade'] * item_existente['preco_unitario']
                                else:
                                    # CORREÇÃO: Garantir que o preço seja float
                                    preco_unitario = float(produto[5])
                                    item = {
                                        'produto_id': produto_id,
                                        'nome': produto[1],
                                        'tamanho': produto[3],
                                        'cor': produto[4],
                                        'quantidade': quantidade,
                                        'preco_unitario': preco_unitario,
                                        'subtotal': preco_unitario * quantidade
                                    }
                                    st.session_state.itens_venda.append(item)
                                
                                st.success("✅ Item adicionado!")
                                st.rerun()
                    
                    # Mostrar itens adicionados
                    if 'itens_venda' in st.session_state and st.session_state.itens_venda:
                        st.subheader("📋 Itens da Venda")
                        total_venda = sum(item['subtotal'] for item in st.session_state.itens_venda)
                        
                        for i, item in enumerate(st.session_state.itens_venda):
                            col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])
                            with col1:
                                st.write(f"**{item['nome']}**")
                                st.write(f"Tamanho: {item['tamanho']} | Cor: {item['cor']}")
                            with col2:
                                st.write(f"Qtd: {item['quantidade']}")
                            with col3:
                                st.write(f"R$ {item['preco_unitario']:.2f}")
                            with col4:
                                st.write(f"R$ {item['subtotal']:.2f}")
                            with col5:
                                if st.button("❌ Remover", key=f"del_venda_{i}"):
                                    st.session_state.itens_venda.pop(i)
                                    st.rerun()
                        
                        st.success(f"**💰 Total da Venda: R$ {total_venda:.2f}**")
                        
                        # Informações adicionais da venda
                        col1, col2 = st.columns(2)
                        with col1:
                            data_entrega = st.date_input("📅 Data de Entrega Prevista", min_value=date.today())
                            forma_pagamento = st.selectbox(
                                "💳 Forma de Pagamento",
                                ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Transferência"]
                            )
                        with col2:
                            observacoes = st.text_area("📝 Observações")
                        
                        if st.button("✅ Finalizar Venda", type="primary", use_container_width=True):
                            if st.session_state.itens_venda:
                                sucesso, resultado = adicionar_pedido_venda(
                                    cliente_id, 
                                    escola_pedido_id,
                                    st.session_state.itens_venda, 
                                    data_entrega, 
                                    forma_pagamento,
                                    observacoes
                                )
                                if sucesso:
                                    st.success(f"✅ Venda #{resultado} realizada com sucesso para {escola_pedido_nome}!")
                                    st.balloons()
                                    del st.session_state.itens_venda
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao realizar venda: {resultado}")
                            else:
                                st.error("❌ Adicione pelo menos um item à venda!")
                    else:
                        st.info("🛒 Adicione itens à venda usando o botão 'Adicionar Item'")
                else:
                    st.error(f"❌ Nenhum produto cadastrado para {escola_pedido_nome}. Cadastre produtos primeiro.")
    
    with tab2:
        st.header("📋 Todas as Vendas")
        vendas = listar_pedidos_por_escola(tipo='venda')
        
        if vendas:
            dados = []
            for venda in vendas:
                status_info = {
                    'Pendente': '🟡 Pendente',
                    'Em produção': '🟠 Em produção', 
                    'Pronto para entrega': '🔵 Pronto para entrega',
                    'Entregue': '🟢 Entregue',
                    'Concluído': '✅ Concluído',
                    'Cancelado': '🔴 Cancelado'
                }.get(venda[3], f'⚪ {venda[3]}')
                
                dados.append({
                    'ID': venda[0],
                    'Escola': venda[12],
                    'Cliente': venda[11],
                    'Status': status_info,
                    'Forma Pagamento': venda[7],
                    'Data Venda': venda[4],
                    'Entrega Prevista': venda[5],
                    'Entrega Real': venda[6] or 'Não entregue',
                    'Quantidade': venda[8],
                    'Valor Total': f"R$ {float(venda[9]):.2f}",
                    'Observações': venda[10] or 'Nenhuma'
                })
            
            df = pd.DataFrame(dados)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("🛒 Nenhuma venda realizada")
    
    with tab3:
        st.header("🔄 Gerenciar Vendas")
        
        vendas = listar_pedidos_por_escola(tipo='venda')
        
        if vendas:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                status_filtro = st.selectbox(
                    "Filtrar por status:",
                    ["Todos"] + list(set(v[3] for v in vendas))
                )
            with col2:
                escola_filtro = st.selectbox(
                    "Filtrar por escola:",
                    ["Todas"] + list(set(v[12] for v in vendas))
                )
            
            # Aplicar filtros
            vendas_filtradas = vendas
            if status_filtro != "Todos":
                vendas_filtradas = [v for v in vendas_filtradas if v[3] == status_filtro]
            if escola_filtro != "Todas":
                vendas_filtradas = [v for v in vendas_filtradas if v[12] == escola_filtro]
            
            for venda in vendas_filtradas:
                with st.expander(f"Venda #{venda[0]} - {venda[11]} - {venda[12]} - R$ {float(venda[9]):.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {venda[11]}")
                        st.write(f"**Escola:** {venda[12]}")
                        st.write(f"**Data da Venda:** {venda[4]}")
                        st.write(f"**Entrega Prevista:** {venda[5]}")
                        if venda[6]:
                            st.write(f"**Entrega Real:** {venda[6]}")
                    
                    with col2:
                        st.write(f"**Status:** {venda[3]}")
                        st.write(f"**Forma de Pagamento:** {venda[7]}")
                        st.write(f"**Quantidade Total:** {venda[8]}")
                        st.write(f"**Valor Total:** R$ {float(venda[9]):.2f}")
                        if venda[10]:
                            st.write(f"**Observações:** {venda[10]}")
                    
                    # Atualizar status
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        novo_status = st.selectbox(
                            "Alterar status:",
                            ["Concluído", "Pronto para entrega", "Entregue", "Cancelado"],
                            key=f"status_venda_{venda[0]}"
                        )
                    with col2:
                        if st.button("🔄 Atualizar", key=f"upd_venda_{venda[0]}"):
                            if novo_status != venda[3]:
                                sucesso, msg = atualizar_status_pedido(venda[0], novo_status)
                                if sucesso:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    
                    # Excluir venda
                    if st.button("🗑️ Excluir Venda", key=f"del_venda_{venda[0]}"):
                        st.warning("⚠️ Esta ação não pode ser desfeita e restaurará o estoque!")
                        if st.button("✅ Confirmar Exclusão", key=f"conf_del_venda_{venda[0]}"):
                            sucesso, msg = excluir_pedido(venda[0])
                            if sucesso:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("🛒 Nenhuma venda para gerenciar")
    
    with tab4:
        st.header("📊 Vendas por Escola")
        
        for escola in escolas:
            with st.expander(f"🏫 {escola[1]}"):
                vendas_escola = listar_pedidos_por_escola(escola[0], tipo='venda')
                
                if vendas_escola:
                    # Métricas da escola
                    col1, col2, col3, col4 = st.columns(4)
                    total_vendas = len(vendas_escola)
                    vendas_concluidas = len([v for v in vendas_escola if v[3] == 'Concluído'])
                    total_valor = sum(float(v[9]) for v in vendas_escola)
                    vendas_entregues = len([v for v in vendas_escola if v[3] == 'Entregue'])
                    
                    with col1:
                        st.metric("Total Vendas", total_vendas)
                    with col2:
                        st.metric("Vendas Concluídas", vendas_concluidas)
                    with col3:
                        st.metric("Total Valor", f"R$ {total_valor:.2f}")
                    with col4:
                        st.metric("Vendas Entregues", vendas_entregues)
                    
                    # Tabela resumida
                    dados = []
                    for venda in vendas_escola:
                        dados.append({
                            'ID': venda[0],
                            'Cliente': venda[11],
                            'Status': venda[3],
                            'Data': venda[4],
                            'Valor': f"R$ {float(venda[9]):.2f}"
                        })
                    
                    st.dataframe(pd.DataFrame(dados), use_container_width=True)
                else:
                    st.info(f"🛒 Nenhuma venda para {escola[1]}")

elif menu == "🏭 Produção":
    escolas = listar_escolas()
    
    if not escolas:
        st.error("❌ Nenhuma escola cadastrada. Configure as escolas primeiro.")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Pedidos em Produção", "📦 Prontos para Entrega", "🔄 Gerenciar Produção", "➕ Novo Pedido Produção"])
    
    with tab1:
        st.header("📋 Pedidos em Produção")
        
        # Filtro por escola
        escola_producao = st.selectbox(
            "🏫 Filtrar por Escola:",
            ["Todas"] + [e[1] for e in escolas],
            key="producao_escola"
        )
        
        # Buscar pedidos em produção
        pedidos_producao = []
        if escola_producao == "Todas":
            for escola in escolas:
                pedidos = listar_pedidos_por_escola(escola[0], tipo='producao')
                pedidos_producao.extend([p for p in pedidos if p[3] == 'Em produção'])
        else:
            escola_id = next(e[0] for e in escolas if e[1] == escola_producao)
            pedidos = listar_pedidos_por_escola(escola_id, tipo='producao')
            pedidos_producao = [p for p in pedidos if p[3] == 'Em produção']
        
        if pedidos_producao:
            for pedido in pedidos_producao:
                with st.expander(f"Pedido #{pedido[0]} - {pedido[11]} - {pedido[12]} - 💰 R$ {float(pedido[9]):.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido[11]}")
                        st.write(f"**Escola:** {pedido[12]}")
                        st.write(f"**Data do Pedido:** {pedido[4]}")
                        st.write(f"**Entrega Prevista:** {pedido[5]}")
                    
                    with col2:
                        st.write(f"**Quantidade Total:** {pedido[8]}")
                        st.write(f"**Valor Total:** R$ {float(pedido[9]):.2f}")
                        if pedido[10]:
                            st.write(f"**Observações:** {pedido[10]}")
                    
                    # Itens do pedido
                    st.subheader("📦 Itens para Produzir")
                    conn = get_connection()
                    if conn:
                        try:
                            cur = conn.cursor()
                            cur.execute('''
                                SELECT pi.quantidade, p.nome, p.tamanho, p.cor, p.preco
                                FROM pedido_itens pi
                                JOIN produtos p ON pi.produto_id = p.id
                                WHERE pi.pedido_id = ?
                            ''', (pedido[0],))
                            
                            itens = cur.fetchall()
                            for item in itens:
                                st.write(f"- {item[1]} ({item[2]} - {item[3]}) - {item[0]} unidades - R$ {item[4]:.2f}")
                        finally:
                            conn.close()
                    
                    # Botão para finalizar produção
                    if st.button("✅ Finalizar Produção", key=f"finalizar_{pedido[0]}"):
                        sucesso, msg = finalizar_pedido_producao(pedido[0])
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("🎉 Nenhum pedido em produção no momento!")
    
    with tab2:
        st.header("📦 Prontos para Entrega")
        
        # Buscar pedidos prontos para entrega
        pedidos_prontos = []
        for escola in escolas:
            pedidos = listar_pedidos_por_escola(escola[0], tipo='producao')
            pedidos_prontos.extend([p for p in pedidos if p[3] == 'Pronto para entrega'])
        
        if pedidos_prontos:
            for pedido in pedidos_prontos:
                with st.expander(f"Pedido #{pedido[0]} - {pedido[11]} - {pedido[12]} - 💰 R$ {float(pedido[9]):.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido[11]}")
                        st.write(f"**Escola:** {pedido[12]}")
                        st.write(f"**Data do Pedido:** {pedido[4]}")
                        st.write(f"**Entrega Prevista:** {pedido[5]}")
                    
                    with col2:
                        st.write(f"**Quantidade Total:** {pedido[8]}")
                        st.write(f"**Valor Total:** R$ {float(pedido[9]):.2f}")
                        if pedido[10]:
                            st.write(f"**Observações:** {pedido[10]}")
                    
                    # Itens do pedido
                    st.subheader("📦 Itens Prontos")
                    conn = get_connection()
                    if conn:
                        try:
                            cur = conn.cursor()
                            cur.execute('''
                                SELECT pi.quantidade, p.nome, p.tamanho, p.cor, p.preco
                                FROM pedido_itens pi
                                JOIN produtos p ON pi.produto_id = p.id
                                WHERE pi.pedido_id = ?
                            ''', (pedido[0],))
                            
                            itens = cur.fetchall()
                            for item in itens:
                                st.write(f"- {item[1]} ({item[2]} - {item[3]}) - {item[0]} unidades - R$ {item[4]:.2f}")
                        finally:
                            conn.close()
                    
                    # Botão para entregar
                    if st.button("🚚 Entregar Pedido", key=f"entregar_{pedido[0]}"):
                        sucesso, msg = entregar_pedido_producao(pedido[0])
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("📦 Nenhum pedido pronto para entrega")
    
    with tab3:
        st.header("🔄 Gerenciar Produção")
        
        producao = listar_pedidos_por_escola(tipo='producao')
        
        if producao:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                status_filtro = st.selectbox(
                    "Filtrar por status:",
                    ["Todos"] + list(set(p[3] for p in producao)),
                    key="filtro_producao"
                )
            with col2:
                escola_filtro = st.selectbox(
                    "Filtrar por escola:",
                    ["Todas"] + list(set(p[12] for p in producao)),
                    key="filtro_escola_producao"
                )
            
            # Aplicar filtros
            producao_filtrada = producao
            if status_filtro != "Todos":
                producao_filtrada = [p for p in producao_filtrada if p[3] == status_filtro]
            if escola_filtro != "Todas":
                producao_filtrada = [p for p in producao_filtrada if p[12] == escola_filtro]
            
            for pedido in producao_filtrada:
                with st.expander(f"Pedido #{pedido[0]} - {pedido[11]} - {pedido[12]} - {pedido[3]} - R$ {float(pedido[9]):.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido[11]}")
                        st.write(f"**Escola:** {pedido[12]}")
                        st.write(f"**Data do Pedido:** {pedido[4]}")
                        st.write(f"**Entrega Prevista:** {pedido[5]}")
                        if pedido[6]:
                            st.write(f"**Entrega Real:** {pedido[6]}")
                    
                    with col2:
                        st.write(f"**Status:** {pedido[3]}")
                        st.write(f"**Quantidade Total:** {pedido[8]}")
                        st.write(f"**Valor Total:** R$ {float(pedido[9]):.2f}")
                        if pedido[10]:
                            st.write(f"**Observações:** {pedido[10]}")
                    
                    # Ações por status
                    if pedido[3] == 'Em produção':
                        if st.button("✅ Finalizar Produção", key=f"finalizar_ger_{pedido[0]}"):
                            sucesso, msg = finalizar_pedido_producao(pedido[0])
                            if sucesso:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    elif pedido[3] == 'Pronto para entrega':
                        if st.button("🚚 Entregar", key=f"entregar_ger_{pedido[0]}"):
                            sucesso, msg = entregar_pedido_producao(pedido[0])
                            if sucesso:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    # Excluir pedido
                    if st.button("🗑️ Excluir Pedido", key=f"del_prod_{pedido[0]}"):
                        st.warning("⚠️ Esta ação não pode ser desfeita!")
                        if st.button("✅ Confirmar Exclusão", key=f"conf_del_prod_{pedido[0]}"):
                            sucesso, msg = excluir_pedido(pedido[0])
                            if sucesso:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("🏭 Nenhum pedido de produção")
    
    with tab4:
        st.header("➕ Novo Pedido de Produção")
        
        # Seleção da escola para o pedido
        escola_producao_nome = st.selectbox(
            "🏫 Escola da Produção:",
            [e[1] for e in escolas],
            key="nova_producao_escola"
        )
        escola_producao_id = next(e[0] for e in escolas if e[1] == escola_producao_nome)
        
        # Selecionar cliente
        clientes = listar_clientes()
        if not clientes:
            st.error("❌ Nenhum cliente cadastrado. Cadastre clientes primeiro.")
        else:
            cliente_selecionado = st.selectbox(
                "👤 Selecione o cliente:",
                [f"{c[1]} (ID: {c[0]})" for c in clientes],
                key="cliente_producao"
            )
            
            if cliente_selecionado:
                cliente_id = int(cliente_selecionado.split("(ID: ")[1].replace(")", ""))
                
                # Produtos da escola selecionada
                produtos = listar_produtos_por_escola(escola_producao_id)
                
                if produtos:
                    st.subheader(f"🏭 Produtos para Produção - {escola_producao_nome}")
                    
                    # Interface para adicionar itens
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        produto_selecionado = st.selectbox(
                            "Produto:",
                            [f"{p[1]} - Tamanho: {p[3]} - Cor: {p[4]} - R$ {p[5]:.2f}" for p in produtos],
                            key="produto_producao"
                        )
                    with col2:
                        quantidade = st.number_input("Quantidade", min_value=1, value=1, key="qtd_producao")
                    with col3:
                        if st.button("➕ Adicionar Item", use_container_width=True, key="add_producao"):
                            if 'itens_producao' not in st.session_state:
                                st.session_state.itens_producao = []
                            
                            produto_id = next(p[0] for p in produtos if f"{p[1]} - Tamanho: {p[3]} - Cor: {p[4]} - R$ {p[5]:.2f}" == produto_selecionado)
                            produto = next(p for p in produtos if p[0] == produto_id)
                            
                            # Verificar se produto já está no pedido
                            item_existente = next((i for i in st.session_state.itens_producao if i['produto_id'] == produto_id), None)
                            
                            if item_existente:
                                item_existente['quantidade'] += quantidade
                                item_existente['subtotal'] = item_existente['quantidade'] * item_existente['preco_unitario']
                            else:
                                # CORREÇÃO: Garantir que o preço seja float
                                preco_unitario = float(produto[5])
                                item = {
                                    'produto_id': produto_id,
                                    'nome': produto[1],
                                    'tamanho': produto[3],
                                    'cor': produto[4],
                                    'quantidade': quantidade,
                                    'preco_unitario': preco_unitario,
                                    'subtotal': preco_unitario * quantidade
                                }
                                st.session_state.itens_producao.append(item)
                            
                            st.success("✅ Item adicionado à produção!")
                            st.rerun()
                    
                    # Mostrar itens adicionados
                    if 'itens_producao' in st.session_state and st.session_state.itens_producao:
                        st.subheader("📋 Itens da Produção")
                        total_producao = sum(item['subtotal'] for item in st.session_state.itens_producao)
                        
                        for i, item in enumerate(st.session_state.itens_producao):
                            col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])
                            with col1:
                                st.write(f"**{item['nome']}**")
                                st.write(f"Tamanho: {item['tamanho']} | Cor: {item['cor']}")
                            with col2:
                                st.write(f"Qtd: {item['quantidade']}")
                            with col3:
                                st.write(f"R$ {item['preco_unitario']:.2f}")
                            with col4:
                                st.write(f"R$ {item['subtotal']:.2f}")
                            with col5:
                                if st.button("❌ Remover", key=f"del_producao_{i}"):
                                    st.session_state.itens_producao.pop(i)
                                    st.rerun()
                        
                        st.success(f"**💰 Total da Produção: R$ {total_producao:.2f}**")
                        
                        # Informações adicionais da produção
                        col1, col2 = st.columns(2)
                        with col1:
                            data_entrega = st.date_input("📅 Data de Entrega Prevista", min_value=date.today(), key="data_producao")
                        with col2:
                            observacoes = st.text_area("📝 Observações", key="obs_producao")
                        
                        if st.button("✅ Criar Pedido de Produção", type="primary", use_container_width=True):
                            if st.session_state.itens_producao:
                                sucesso, resultado = adicionar_pedido_producao(
                                    cliente_id, 
                                    escola_producao_id,
                                    st.session_state.itens_producao, 
                                    data_entrega,
                                    observacoes
                                )
                                if sucesso:
                                    st.success(f"✅ Pedido de produção #{resultado} criado com sucesso para {escola_producao_nome}!")
                                    st.balloons()
                                    del st.session_state.itens_producao
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao criar pedido de produção: {resultado}")
                            else:
                                st.error("❌ Adicione pelo menos um item à produção!")
                    else:
                        st.info("🏭 Adicione itens à produção usando o botão 'Adicionar Item'")
                else:
                    st.error(f"❌ Nenhum produto cadastrado para {escola_producao_nome}. Cadastre produtos primeiro.")

elif menu == "📈 Relatórios":
    escolas = listar_escolas()
    
    tab1, tab2, tab3 = st.tabs(["📊 Vendas por Escola", "📦 Produtos Mais Vendidos", "👥 Análise Completa"])
    
    with tab1:
        st.header("📊 Relatório de Vendas por Escola")
        
        escola_relatorio = st.selectbox(
            "Selecione a escola:",
            ["Todas as escolas"] + [e[1] for e in escolas],
            key="relatorio_escola"
        )
        
        if escola_relatorio == "Todas as escolas":
            relatorio_vendas = gerar_relatorio_vendas_por_escola()
        else:
            escola_id = next(e[0] for e in escolas if e[1] == escola_relatorio)
            relatorio_vendas = gerar_relatorio_vendas_por_escola(escola_id)
        
        if not relatorio_vendas.empty:
            st.dataframe(relatorio_vendas, use_container_width=True)
            
            # Gráfico de vendas
            if escola_relatorio == "Todas as escolas":
                fig = px.line(relatorio_vendas, x='Data', y='Total Vendas (R$)', color='Escola',
                             title='Evolução das Vendas por Escola')
            else:
                fig = px.line(relatorio_vendas, x='Data', y='Total Vendas (R$)', 
                             title=f'Evolução das Vendas - {escola_relatorio}')
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas resumidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Período", f"R$ {relatorio_vendas['Total Vendas (R$)'].sum():.2f}")
            with col2:
                st.metric("Média Diária", f"R$ {relatorio_vendas['Total Vendas (R$)'].mean():.2f}")
            with col3:
                st.metric("Maior Venda", f"R$ {relatorio_vendas['Total Vendas (R$)'].max():.2f}")
        else:
            st.info("📊 Nenhum dado de venda disponível")
    
    with tab2:
        st.header("📦 Produtos Mais Vendidos")
        
        escola_produtos = st.selectbox(
            "Selecione a escola:",
            ["Todas as escolas"] + [e[1] for e in escolas],
            key="produtos_relatorio"
        )
        
        if escola_produtos == "Todas as escolas":
            relatorio_produtos = gerar_relatorio_produtos_por_escola()
        else:
            escola_id = next(e[0] for e in escolas if e[1] == escola_produtos)
            relatorio_produtos = gerar_relatorio_produtos_por_escola(escola_id)
        
        if not relatorio_produtos.empty:
            st.dataframe(relatorio_produtos, use_container_width=True)
            
            # Gráfico de produtos mais vendidos
            top_produtos = relatorio_produtos.head(10)
            if escola_produtos == "Todas as escolas":
                fig = px.bar(top_produtos, x='Produto', y='Total Vendido', color='Escola',
                            title='Top 10 Produtos Mais Vendidos')
            else:
                fig = px.bar(top_produtos, x='Produto', y='Total Vendido',
                            title=f'Top 10 Produtos Mais Vendidos - {escola_produtos}')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📦 Nenhum dado de produto vendido disponível")
    
    with tab3:
        st.header("👥 Análise Completa do Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🏫 Escolas")
            escolas_count = len(escolas)
            st.metric("Total de Escolas", escolas_count)
            
        with col2:
            st.subheader("👥 Clientes")
            clientes = listar_clientes()
            st.metric("Total de Clientes", len(clientes))
            
        with col3:
            st.subheader("👕 Produtos")
            total_produtos = 0
            for escola in escolas:
                produtos = listar_produtos_por_escola(escola[0])
                total_produtos += len(produtos)
            st.metric("Total de Produtos", total_produtos)
        
        # Resumo por escola
        st.subheader("📋 Resumo por Escola")
        resumo_data = []
        for escola in escolas:
            produtos_escola = listar_produtos_por_escola(escola[0])
            vendas_escola = listar_pedidos_por_escola(escola[0], tipo='venda')
            producao_escola = listar_pedidos_por_escola(escola[0], tipo='producao')
            total_vendas = sum(float(v[9]) for v in vendas_escola)
            
            resumo_data.append({
                'Escola': escola[1],
                'Produtos': len(produtos_escola),
                'Vendas': len(vendas_escola),
                'Produção': len(producao_escola),
                'Vendas (R$)': total_vendas
            })
        
        if resumo_data:
            st.dataframe(pd.DataFrame(resumo_data), use_container_width=True)
            
            # Gráfico de comparação entre escolas
            fig = px.bar(pd.DataFrame(resumo_data), x='Escola', y='Vendas (R$)',
                        title='Comparação de Vendas por Escola')
            st.plotly_chart(fig, use_container_width=True)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("👕 Sistema de Fardamentos v13.0\n\n✅ **FLUXO CORRETO DE PRODUÇÃO**\n🏭 Pedido → Produção → Estoque → Entrega\n🛒 Vendas diretas do estoque")

# Botão para recarregar dados
if st.sidebar.button("🔄 Recarregar Dados"):
    st.rerun()
