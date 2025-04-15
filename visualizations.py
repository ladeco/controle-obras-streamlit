import plotly.graph_objects as go
import pandas as pd

def plot_comparativo_orcamento_gasto_projeto(df_comparativo):
    """Gera um gráfico de barras comparando o orçamento total e o gasto total por projeto."""
    fig = go.Figure(data=[
        go.Bar(name='Orçamento Total', x=df_comparativo['Projeto'], y=df_comparativo['total_orcado']),
        go.Bar(name='Gasto Total', x=df_comparativo['Projeto'], y=df_comparativo['total_gasto'])
    ])
    # Layout do gráfico
    fig.update_layout(
        title='Comparativo de Orçamento vs. Gasto Total por Projeto',
        xaxis_title='Projeto',
        yaxis_title='Valor Total (R$)',
        barmode='group' # Para mostrar as barras lado a lado
    )
    return fig

def plot_gasto_por_classificacao(df_gasto_classificacao):
    """Gera um gráfico de barras horizontais mostrando o gasto por classificação."""
    fig = go.Figure(data=[go.Bar(
        x=df_gasto_classificacao['total_gasto'],
        y=df_gasto_classificacao['classificacao'],
        orientation='h'
    )])
    fig.update_layout(
        title='Gasto por Classificação',
        xaxis_title='Valor Total Gasto (R$)',
        yaxis_title='Classificação'
    )
    return fig

def plot_gasto_por_fornecedor(df_gasto_fornecedor):
    """Gera um gráfico de barras horizontais mostrando o gasto por fornecedor."""
    fig = go.Figure(data=[go.Bar(
        x=df_gasto_fornecedor['total_gasto'],
        y=df_gasto_fornecedor['fornecedor'],
        orientation='h'
    )])
    fig.update_layout(
        title='Gasto por Fornecedor',
        xaxis_title='Valor Total Gasto (R$)',
        yaxis_title='Fornecedor'
    )
    return fig

def plot_gastos_mensais(df_gastos_mensais, orcamento_total, classificacao_filtrada=None):
    """Gera um gráfico de barras verticais mostrando os gastos mensais e a linha de orçamento."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_gastos_mensais['mes_ano'],
        y=df_gastos_mensais['total_gasto'],
        name='Gasto Mensal' + (f' ({classificacao_filtrada})' if classificacao_filtrada else '')
    ))
    fig.add_trace(go.Scatter(
        x=df_gastos_mensais['mes_ano'],
        y=[orcamento_total] * len(df_gastos_mensais),
        mode='lines',
        name='Orçamento Total do Projeto',
        line=dict(color='red', dash='dash')
    ))
    fig.update_layout(
        title='Evolução Mensal de Gastos vs. Orçamento',
        xaxis_title='Mês/Ano',
        yaxis_title='Valor Total (R$)',
        barmode='group'
    )
    return fig