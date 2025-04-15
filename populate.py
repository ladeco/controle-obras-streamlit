import sqlite3
import random
from datetime import datetime, timedelta
import database  # Importa seu arquivo database.py

DATABASE_NAME = 'obra_controle.db'

def gerar_data_aleatoria(start_date, end_date):
    """Gera uma data aleatória entre duas datas."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def popular_banco():
    conn = database.create_connection()
    cursor = conn.cursor()

    # Limpar tabelas existentes (opcional, para recomeçar com dados novos)
    cursor.execute("DELETE FROM lancamentos")
    cursor.execute("DELETE FROM orcamentos")
    cursor.execute("DELETE FROM projetos")
    cursor.execute("DELETE FROM fornecedores")
    conn.commit()

    # Criar fornecedores genéricos
    for i in range(5):
        database.salvar_fornecedor(conn, f"Fornecedor {i+1}", f"CNPJ{i+1}", f"1111-111{i}", f"email{i}@email.com", f"Endereço {i+1}")

    # Criar projetos
    projetos_data = [
        {"nome": "Projeto Alfa (Concluindo)", "inicio": datetime(2024, 10, 1), "duracao_meses": 6},
        {"nome": "Projeto Beta (Em Andamento)", "inicio": datetime(2025, 1, 1), "duracao_meses": 4},
        {"nome": "Projeto Gama (Início)", "inicio": datetime(2025, 4, 1), "duracao_meses": 1},
    ]

    projetos_ids = []
    for proj in projetos_data:
        fim = proj["inicio"] + timedelta(days=proj["duracao_meses"] * 30)
        database.salvar_projeto(conn, proj["nome"], "Descrição do projeto", proj["inicio"].date(), fim.date())
        projetos_ids.append(cursor.lastrowid)

    categorias_orcamento = ["Aluminio", "Material", "Pintura", "Vidros", "Beneficiamento", "Projetos", "Adiantamentos", "Instalacao"]

    # Gerar orçamentos aleatórios
    for projeto_id in projetos_ids:
        for categoria in categorias_orcamento:
            valor_orcado = round(random.uniform(5000, 50000), 2)
            database.salvar_orcamento(conn, projeto_id, categoria, valor_orcado)

    # Gerar lançamentos aleatórios
    for projeto_id in projetos_ids:
        projeto_info = next(p for i, p in enumerate(projetos_data) if i == projetos_ids.index(projeto_id))
        data_inicio = projeto_info["inicio"]
        data_fim = data_inicio + timedelta(days=projeto_info["duracao_meses"] * 30)
        num_lancamentos = random.randint(20, 50)
        for _ in range(num_lancamentos):
            data_lancamento = gerar_data_aleatoria(data_inicio, data_fim).date()
            classificacao = random.choice(categorias_orcamento)
            fornecedor_id = random.randint(1, 5)
            valor_faturado = round(random.uniform(100, 10000), 2)
            database.salvar_lancamento(conn, projeto_id, data_lancamento, classificacao, data_lancamento, f"DOC{random.randint(100, 999)}", fornecedor_id, f"Despesa com {classificacao}", valor_faturado)

    conn.close()
    print("Banco de dados populado com dados de teste.")

if __name__ == "__main__":
    popular_banco()