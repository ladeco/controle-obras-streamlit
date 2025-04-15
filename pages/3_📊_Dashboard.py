import streamlit as st
import database
import visualizations
import pandas as pd

st.title("Dashboard")

conn = database.create_connection()

# Gráfico de Comparativo Orçamento vs. Gasto Total por Projeto
st.subheader("Comparativo Orçamento vs. Gasto Total por Projeto")
df_comparativo_projetos = database.get_comparativo_orcamento_gasto_por_projeto(conn)
if not df_comparativo_projetos.empty:
    fig_comparativo_projetos = visualizations.plot_comparativo_orcamento_gasto_projeto(df_comparativo_projetos)
    st.plotly_chart(fig_comparativo_projetos)
else:
    st.info("Nenhum projeto cadastrado para exibir o comparativo de orçamento vs. gasto.")

# Gráfico de Gasto por Classificação
st.subheader("Gasto por Classificação")
df_gasto_classificacao = database.get_gasto_por_classificacao(conn)
if not df_gasto_classificacao.empty:
    fig_gasto_classificacao = visualizations.plot_gasto_por_classificacao(df_gasto_classificacao)
    st.plotly_chart(fig_gasto_classificacao)
else:
    st.info("Nenhum lançamento cadastrado para exibir o gasto por classificação.")

# Gráfico de Gasto por Fornecedor
st.subheader("Gasto por Fornecedor")
df_gasto_por_fornecedor = database.get_gasto_por_fornecedor(conn)
if not df_gasto_por_fornecedor.empty:
    fig_gasto_por_fornecedor = visualizations.plot_gasto_por_fornecedor(df_gasto_por_fornecedor)
    st.plotly_chart(fig_gasto_por_fornecedor)
else:
    st.info("Nenhum lançamento cadastrado para exibir o gasto por fornecedor.")

# Gráfico de Evolução Mensal de Gastos vs. Orçamento
st.subheader("Evolução Mensal de Gastos vs. Orçamento")
df_projetos_gastos_mensais = database.get_projetos(conn)
projetos_dict_gastos_mensais = df_projetos_gastos_mensais.set_index('id')['nome'].to_dict()
projetos_nomes_gastos_mensais = list(projetos_dict_gastos_mensais.values())
projeto_selecionado_nome_gastos_mensais = st.selectbox("Selecionar Projeto para Análise Mensal:", projetos_nomes_gastos_mensais, key="selectbox_gastos_mensais_projeto")
projeto_selecionado_id_gastos_mensais = [k for k, v in projetos_dict_gastos_mensais.items() if v == projeto_selecionado_nome_gastos_mensais][0] if projetos_dict_gastos_mensais else None

if projeto_selecionado_id_gastos_mensais:
    # Filtro por Classificação
    classificacoes = pd.read_sql_query("SELECT DISTINCT classificacao FROM lancamentos", conn)['classificacao'].tolist()
    classificacao_selecionada = st.selectbox("Filtrar por Classificação (opcional):", ["Todas"] + classificacoes, key="selectbox_filtro_classificacao")
    filtro_classificacao = classificacao_selecionada if classificacao_selecionada != "Todas" else None

    df_gastos_mensais = database.get_gastos_mensais(conn, filtro_classificacao)
    orcamento_total = database.get_orcamento_total_projeto(conn, projeto_selecionado_id_gastos_mensais)

    if not df_gastos_mensais.empty:
        fig_gastos_mensais = visualizations.plot_gastos_mensais(df_gastos_mensais, orcamento_total, filtro_classificacao)
        st.plotly_chart(fig_gastos_mensais)
    else:
        st.info(f"Nenhum lançamento encontrado para o projeto '{projeto_selecionado_nome_gastos_mensais}'" + (f" e classificação '{filtro_classificacao}'" if filtro_classificacao else "") + ".")
else:
    st.info("Selecione um projeto para exibir a evolução mensal de gastos.")

conn.close()