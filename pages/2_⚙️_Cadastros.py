import streamlit as st
import database
import pandas as pd

st.title("Cadastros")

conn = database.create_connection()
database.create_tables(conn) # Garante que as tabelas existem

with st.expander("Cadastrar Fornecedor"):
    st.subheader("Cadastro de Fornecedores")
    with st.form("novo_fornecedor"):
        nome_fornecedor = st.text_input("Nome do Fornecedor:")
        cnpj_fornecedor = st.text_input("CNPJ (opcional):")
        telefone_fornecedor = st.text_input("Telefone (opcional):")
        email_fornecedor = st.text_input("Email (opcional):")
        endereco_fornecedor = st.text_area("Endereço (opcional):")
        submitted_fornecedor = st.form_submit_button("Salvar Fornecedor")
        if submitted_fornecedor:
            if nome_fornecedor:
                if database.salvar_fornecedor(conn, nome_fornecedor, cnpj_fornecedor, telefone_fornecedor, email_fornecedor, endereco_fornecedor):
                    st.success(f"Fornecedor '{nome_fornecedor}' cadastrado com sucesso!")
                else:
                    st.error(f"Erro ao cadastrar o fornecedor.")
            else:
                st.error("O nome do fornecedor é obrigatório.")
    st.subheader("Fornecedores Cadastrados")
    df_fornecedores = database.get_fornecedores(conn)
    st.dataframe(df_fornecedores)

with st.expander("Cadastrar Projeto"):
    st.title("Cadastro de Projetos")
    with st.form("novo_projeto"):
        nome_projeto = st.text_input("Nome do Projeto:")
        descricao_projeto = st.text_area("Descrição:")
        data_inicio_projeto = st.date_input("Data de Início:")
        data_fim_prevista_projeto = st.date_input("Data de Fim Prevista:")
        submitted_projeto = st.form_submit_button("Salvar Projeto")
        if submitted_projeto:
            if nome_projeto:
                if database.salvar_projeto(conn, nome_projeto, descricao_projeto, data_inicio_projeto, data_fim_prevista_projeto):
                    st.success(f"Projeto '{nome_projeto}' cadastrado com sucesso!")
                else:
                    st.error(f"Erro ao cadastrar o projeto.")
            else:
                st.error("O nome do projeto é obrigatório.")
    st.subheader("Projetos Cadastrados")
    df_projetos = database.get_projetos(conn)
    st.dataframe(df_projetos)

    projetos_dict = df_projetos.set_index('id')['nome'].to_dict()
    projetos_nomes = list(projetos_dict.values())

with st.expander("Cadastrar Lançamento"):
    st.subheader("Cadastro de Lançamentos")
    projeto_selecionado_nome_lancamento = st.selectbox("Selecionar Projeto para Lançamento:", projetos_nomes, key="selectbox_lancamento_projeto_cadastro")
    projeto_selecionado_id_lancamento = [k for k, v in projetos_dict.items() if v == projeto_selecionado_nome_lancamento][0] if projetos_dict else None

    if projeto_selecionado_id_lancamento:
        # Buscar categorias de orçamento para o projeto selecionado
        df_categorias_orcamento = database.get_orcamentos_por_projeto(conn, projeto_selecionado_id_lancamento)
        categorias_orcamento = df_categorias_orcamento['categoria'].tolist()

        with st.form("novo_lancamento"):
            data_lancamento = st.date_input("Data do Lançamento:")
            # Usar selectbox para classificação
            classificacao = st.selectbox("Classificação:", categorias_orcamento)
            emissao = st.date_input("Data de Emissão (opcional):", value=None)
            documento = st.text_input("Documento (NF, Recibo, etc.):")
            df_fornecedores_lancamento = database.get_fornecedores(conn)
            fornecedores_dict = df_fornecedores_lancamento.set_index('id')['nome'].to_dict()
            fornecedores_nomes = list(fornecedores_dict.values())
            fornecedor_selecionado_nome = st.selectbox("Fornecedor:", fornecedores_nomes)
            fornecedor_selecionado_id = [k for k, v in fornecedores_dict.items() if v == fornecedor_selecionado_nome][0] if fornecedores_dict else None
            descricao = st.text_area("Descrição:")
            valor_faturado = st.number_input("Valor Faturado:")
            submitted_lancamento = st.form_submit_button("Salvar Lançamento")
            if submitted_lancamento:
                if classificacao and valor_faturado is not None and fornecedor_selecionado_id:
                    if database.salvar_lancamento(conn, projeto_selecionado_id_lancamento, data_lancamento, classificacao, emissao, documento, fornecedor_selecionado_id, descricao, valor_faturado):
                        st.success(f"Lançamento para o projeto '{projeto_selecionado_nome_lancamento}' com a classificação '{classificacao}' cadastrado com sucesso!")
                    else:
                        st.error(f"Erro ao cadastrar o lançamento.")
                elif not fornecedor_selecionado_id:
                    st.error("Selecione um fornecedor para o lançamento.")
                else:
                    st.error("A classificação e o valor faturado são obrigatórios.")
    else:
        st.warning("Cadastre um projeto primeiro para poder adicionar lançamentos.")
    st.subheader("Lançamentos Cadastrados")
    if projeto_selecionado_id_lancamento:
        df_lancamentos = database.get_lancamentos_por_projeto(conn, projeto_selecionado_id_lancamento)
        st.dataframe(df_lancamentos)
    else:
        st.info("Selecione um projeto para ver os lançamentos.")

with st.expander("Cadastrar Orçamento"):
    st.title("Cadastro de Orçamento por Projeto")
    projeto_selecionado_nome_orcamento = st.selectbox("Selecionar Projeto para Cadastrar Orçamento:", projetos_nomes, key="selectbox_orcamento_projeto_cadastro")
    projeto_selecionado_id_orcamento = [k for k, v in projetos_dict.items() if v == projeto_selecionado_nome_orcamento][0] if projetos_dict else None

    if projeto_selecionado_id_orcamento:
        st.subheader(f"Orçamento para o Projeto: {projeto_selecionado_nome_orcamento}")
        categorias_orcamento = {
            "Aluminio": st.number_input("Alumínio:", min_value=0.0, key=f"orc_alu_{projeto_selecionado_id_orcamento}_cadastro"),
            "Material": st.number_input("Material:", min_value=0.0, key=f"orc_mat_{projeto_selecionado_id_orcamento}_cadastro"),
            "Pintura": st.number_input("Pintura:", min_value=0.0, key=f"orc_pin_{projeto_selecionado_id_orcamento}_cadastro"),
            "Vidros": st.number_input("Vidros:", min_value=0.0, key=f"orc_vid_{projeto_selecionado_id_orcamento}_cadastro"),
            "Beneficiamento": st.number_input("Beneficiamento:", min_value=0.0, key=f"orc_ben_{projeto_selecionado_id_orcamento}_cadastro"),
            "Projetos": st.number_input("Projetos (custo da empresa):", min_value=0.0, key=f"orc_pro_{projeto_selecionado_id_orcamento}_cadastro"),
            "Adiantamentos": st.number_input("Adiantamentos (custo da empresa):", min_value=0.0, key=f"orc_adi_{projeto_selecionado_id_orcamento}_cadastro"),
            "Instalacao": st.number_input("Instalação (custo da empresa):", min_value=0.0, key=f"orc_ins_{projeto_selecionado_id_orcamento}_cadastro"),
        }

        if st.button("Salvar Orçamento"):
            for categoria, valor in categorias_orcamento.items():
                database.salvar_orcamento(conn, projeto_selecionado_id_orcamento, categoria, valor)
            st.success(f"Orçamento para o projeto '{projeto_selecionado_nome_orcamento}' salvo com sucesso!")
    else:
        st.info("Selecione um projeto para cadastrar o orçamento.")

    st.subheader("Orçamentos Cadastrados")
    df_orcamentos = pd.read_sql_query("SELECT p.nome as projeto_nome, o.categoria, o.valor_orcado FROM orcamentos o JOIN projetos p ON o.projeto_id = p.id", conn)
    st.dataframe(df_orcamentos)

conn.close()