import streamlit as st
import database

st.title("Visão Geral dos Projetos")

conn = database.create_connection()

df_projetos_resumo = database.get_resumo_projetos(conn)
if not df_projetos_resumo.empty:
    st.dataframe(df_projetos_resumo)
else:
    st.info("Nenhum projeto cadastrado.")

conn.close()