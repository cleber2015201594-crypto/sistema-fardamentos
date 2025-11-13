# =========================================
# 🗄️ SISTEMA HÍBRIDO - SUPABASE + LOCAL
# =========================================

# Importar configurações do Supabase
try:
    from database.supabase_config import (
        get_supabase, salvar_fardamento, buscar_fardamentos,
        atualizar_fardamento, excluir_fardamento, salvar_pedido,
        buscar_pedidos, salvar_cliente, buscar_clientes, sistema_hibrido
    )
    SUPABASE_DISPONIVEL = True
except Exception as e:
    SUPABASE_DISPONIVEL = False
    st.sidebar.warning(f"🗄️ Modo Local Ativo")

# Verificar status do banco
if SUPABASE_DISPONIVEL:
    try:
        status, conectado = sistema_hibrido()
        st.sidebar.info(status)
    except Exception as e:
        st.sidebar.error(f"❌ Erro no Supabase: {e}")
        SUPABASE_DISPONIVEL = False
else:
    st.sidebar.warning("🗄️ Modo Local Ativo")
