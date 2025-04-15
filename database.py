import sqlite3
import pandas as pd

DATABASE_NAME = 'obra_controle.db'

def create_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def create_tables(conn):
    """Cria as tabelas no banco de dados se não existirem."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            data_inicio DATE,
            data_fim_prevista DATE,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            data_lancamento DATE NOT NULL,
            classificacao TEXT NOT NULL,
            emissao DATE,
            documento TEXT,
            fornecedor_id INTEGER,
            descricao TEXT,
            valor_faturado REAL NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            valor_orcado REAL NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
            UNIQUE (projeto_id, categoria)
        )
    ''')
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS atualiza_data_orcamento
        AFTER UPDATE ON orcamentos
        BEGIN
            UPDATE orcamentos SET data_atualizacao = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW') WHERE id = NEW.id;
        END;
    ''')
    conn.commit()

def salvar_fornecedor(conn, nome, cnpj, telefone, email, endereco):
    """Salva os dados de um novo fornecedor no banco de dados."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO fornecedores (nome, cnpj, telefone, email, endereco) VALUES (?, ?, ?, ?, ?)",
            (nome, cnpj, telefone, email, endereco)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar fornecedor: {e}")
        return False

def get_fornecedores(conn):
    """Retorna todos os fornecedores do banco de dados como um DataFrame."""
    return pd.read_sql_query("SELECT id, nome FROM fornecedores", conn)

def salvar_projeto(conn, nome, descricao, data_inicio, data_fim_prevista):
    """Salva os dados de um novo projeto no banco de dados."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO projetos (nome, descricao, data_inicio, data_fim_prevista) VALUES (?, ?, ?, ?)",
            (nome, descricao, data_inicio.strftime('%Y-%m-%d'), data_fim_prevista.strftime('%Y-%m-%d'))
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar projeto: {e}")
        return False

def get_projetos(conn):
    """Retorna todos os projetos do banco de dados como um DataFrame."""
    return pd.read_sql_query("SELECT id, nome FROM projetos", conn)

def salvar_lancamento(conn, projeto_id, data_lancamento, classificacao, emissao, documento, fornecedor_id, descricao, valor_faturado):
    """Salva os dados de um novo lançamento no banco de dados."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO lancamentos (projeto_id, data_lancamento, classificacao, emissao, documento, fornecedor_id, descricao, valor_faturado) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (projeto_id, data_lancamento.strftime('%Y-%m-%d'), classificacao, emissao.strftime('%Y-%m-%d') if emissao else None, documento, fornecedor_id, descricao, valor_faturado)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar lançamento: {e}")
        return False

def get_lancamentos_por_projeto(conn, projeto_id):
    """Retorna todos os lançamentos de um projeto específico como um DataFrame."""
    return pd.read_sql_query(
        "SELECT l.id, p.nome as projeto_nome, f.nome as fornecedor_nome, l.data_lancamento, l.classificacao, l.valor_faturado FROM lancamentos l JOIN projetos p ON l.projeto_id = p.id LEFT JOIN fornecedores f ON l.fornecedor_id = f.id WHERE l.projeto_id = ?",
        conn,
        params=(projeto_id,)
    )

def salvar_orcamento(conn, projeto_id, categoria, valor_orcado):
    """Salva ou atualiza o orçamento para um projeto e categoria."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO orcamentos (projeto_id, categoria, valor_orcado, data_atualizacao) VALUES (?, ?, ?, STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))",
            (projeto_id, categoria, valor_orcado)
        )
        cursor.execute(
            "UPDATE orcamentos SET valor_orcado = ?, data_atualizacao = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW') WHERE projeto_id = ? AND categoria = ?",
            (valor_orcado, projeto_id, categoria)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar/atualizar orçamento: {e}")
        return False

def get_orcamentos_por_projeto(conn, projeto_id):
    """Retorna os orçamentos de um projeto específico como um DataFrame."""
    return pd.read_sql_query("SELECT categoria, valor_orcado FROM orcamentos WHERE projeto_id = ?", conn, params=(projeto_id,))


def get_gastos_orcamento_projeto(conn, projeto_id):
    """Retorna um DataFrame comparando gastos e orçamento por categoria para um projeto."""
    # Buscar o orçamento do projeto selecionado
    df_orcamento_projeto = pd.read_sql_query(
        "SELECT categoria, valor_orcado FROM orcamentos WHERE projeto_id = ?",
        conn,
        params=(projeto_id,)
    )
    orcamento_projeto = df_orcamento_projeto.set_index('categoria')['valor_orcado'].to_dict()

    # Buscar os gastos do projeto selecionado
    df_gastos_projeto = pd.read_sql_query(
        "SELECT classificacao, SUM(valor_faturado) as total_gasto FROM lancamentos WHERE projeto_id = ? GROUP BY classificacao",
        conn,
        params=(projeto_id,)
    )
    gastos_por_categoria = df_gastos_projeto.set_index('classificacao')['total_gasto'].to_dict()

    categorias_orcamento_lista = ["Aluminio", "Material", "Pintura", "Vidros", "Beneficiamento", "Projetos", "Adiantamentos", "Instalacao"]
    data_relatorio = []

    for categoria in categorias_orcamento_lista:
        orcado = orcamento_projeto.get(categoria, 0)
        gasto = gastos_por_categoria.get(categoria, 0)
        data_relatorio.append({'Categoria': categoria, 'Orçado': orcado, 'Gasto': gasto, 'Variação': orcado - gasto})

    return pd.DataFrame(data_relatorio)

def get_comparativo_orcamento_gasto_por_projeto(conn):
    """Retorna um DataFrame com o comparativo de orçamento e gasto total por projeto."""
    df_orcamento_total = pd.read_sql_query(
        "SELECT projeto_id, SUM(valor_orcado) as total_orcado FROM orcamentos GROUP BY projeto_id",
        conn
    )
    df_gasto_total = pd.read_sql_query(
        "SELECT projeto_id, SUM(valor_faturado) as total_gasto FROM lancamentos GROUP BY projeto_id",
        conn
    )
    df_projetos = pd.read_sql_query("SELECT id, nome FROM projetos", conn)

    df_comparativo = pd.merge(df_projetos, df_orcamento_total, left_on='id', right_on='projeto_id', how='left')
    df_comparativo = pd.merge(df_comparativo, df_gasto_total, on='projeto_id', how='left')

    df_comparativo.rename(columns={'nome': 'Projeto'}, inplace=True)
    df_comparativo.fillna(0, inplace=True)
    df_comparativo = df_comparativo[['Projeto', 'total_orcado', 'total_gasto']]
    return df_comparativo

def get_resumo_projetos(conn):
    """Retorna um DataFrame com o resumo dos projetos (nome, data de início, data de fim prevista)."""
    return pd.read_sql_query(
        "SELECT nome, data_inicio, data_fim_prevista FROM projetos",
        conn
    )

def get_comparativo_orcamento_gasto_por_projeto(conn):
    """Retorna um DataFrame com o comparativo de orçamento e gasto total por projeto."""
    df_orcamento_total = pd.read_sql_query(
        "SELECT projeto_id, SUM(valor_orcado) as total_orcado FROM orcamentos GROUP BY projeto_id",
        conn
    )
    df_gasto_total = pd.read_sql_query(
        "SELECT projeto_id, SUM(valor_faturado) as total_gasto FROM lancamentos GROUP BY projeto_id",
        conn
    )
    df_projetos = pd.read_sql_query("SELECT id, nome FROM projetos", conn)

    df_comparativo = pd.merge(df_projetos, df_orcamento_total, left_on='id', right_on='projeto_id', how='left')
    df_comparativo = pd.merge(df_comparativo, df_gasto_total, on='projeto_id', how='left')

    df_comparativo.rename(columns={'nome': 'Projeto'}, inplace=True)
    df_comparativo.fillna(0, inplace=True)
    df_comparativo = df_comparativo[['Projeto', 'total_orcado', 'total_gasto']]
    return df_comparativo

def get_gasto_por_classificacao(conn):
    """Retorna um DataFrame com o gasto total por classificação."""
    return pd.read_sql_query(
        "SELECT classificacao, SUM(valor_faturado) as total_gasto FROM lancamentos GROUP BY classificacao ORDER BY total_gasto DESC",
        conn
    )


def get_gasto_por_fornecedor(conn):
    """Retorna um DataFrame com o gasto total por fornecedor."""
    return pd.read_sql_query(
        """
        SELECT f.nome as fornecedor, SUM(l.valor_faturado) as total_gasto
        FROM lancamentos l
        JOIN fornecedores f ON l.fornecedor_id = f.id
        GROUP BY f.nome
        ORDER BY total_gasto DESC
        """,
        conn
    )

def get_gastos_mensais(conn, classificacao=None):
    """Retorna um DataFrame com os gastos mensais, opcionalmente filtrado por classificação."""
    query = """
        SELECT STRFTIME('%Y-%m', data_lancamento) as mes_ano, SUM(valor_faturado) as total_gasto
        FROM lancamentos
    """
    params = []
    if classificacao:
        query += " WHERE classificacao = ?"
        params.append(classificacao)
    query += " GROUP BY mes_ano ORDER BY mes_ano"
    return pd.read_sql_query(query, conn, params=params)

def get_orcamento_total_projeto(conn, projeto_id):
    """Retorna o orçamento total de um projeto."""
    df_orcamento = pd.read_sql_query(
        "SELECT SUM(valor_orcado) as total_orcado FROM orcamentos WHERE projeto_id = ?",
        conn,
        params=(projeto_id,)
    )
    return df_orcamento['total_orcado'].iloc[0] if not df_orcamento.empty else 0

# Adicionaremos outras funções aqui conforme avançamos
