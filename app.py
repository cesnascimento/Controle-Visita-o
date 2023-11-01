import streamlit as st
import pandas as pd
from datetime import datetime
import ast
import re

# Carregar os dados
data = pd.read_csv('sharepoint_data.csv')
data['Data'] = pd.to_datetime(data['Data'], errors='coerce')
data['Ruptura'] = data['Ruptura'].apply(lambda x: 'SIM' if x else 'NÃO')

# Opções para o usuário escolher
tab_options = ["Visualização de Visita",
               "Visualização de Ruptura", "Visualização de Imagens"]
chosen_tab = st.radio("Escolha uma aba:", tab_options)

if chosen_tab == "Visualização de Visita":

    st.sidebar.header('Filtros')

    # Filtros e visualização de dados...

    selected_data = st.sidebar.date_input(
        'Selecione a faixa de datas',
        min_value=data['Data'].min().date(),
        max_value=data['Data'].max().date(),
        value=(data['Data'].min().date(), data['Data'].max().date()),
        key='select_data'
    )
    selected_rede = st.sidebar.multiselect(
        'Selecione a(s) rede(s)',
        options=list(data['Rede'].unique()),
        key='select_rede'
    )
    selected_funcao = st.sidebar.multiselect(
        'Selecione a(s) função(ões)',
        options=list(data['Funcao'].unique()),
        key='select_funcao'
    )
    selected_pessoa = st.sidebar.multiselect(
        'Selecione a(s) pessoa(s)',
        options=list(data['Created By'].unique()),
        key='select_pessoa'
    )

    # Conversão e filtros de data...
    start_date = pd.Timestamp(selected_data[0])
    end_date = pd.Timestamp(selected_data[1])
    data = data[(data['Data'] >= start_date) & (data['Data'] <= end_date)]

    if selected_pessoa:
        data = data[data['Created By'].isin(selected_pessoa)]
    if selected_rede:
        data = data[data['Rede'].isin(selected_rede)]
    if selected_funcao:
        data = data[data['Funcao'].isin(selected_funcao)]

    # Prefixo da URL das imagens e função para criar links HTML das imagens...
    img_url_prefix = "https://dermage.sharepoint.com/sites/AdminHomePage/SiteAssets/Lists/a71446a8-a43c-4fde-ab80-a8440de77d91/"

    def create_image_link(row):
        img_html = ""
        for img_col in ['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']:
            img = row[img_col]
            if pd.notna(img):
                img_html += (
                    f'<a href="{img_url_prefix}{img}" target="_blank">'
                    f'<img src="{img_url_prefix}{img}" style="width:100px;"></a>'
                )
        return img_html

    data['Imagens'] = data.apply(create_image_link, axis=1)
    data = data.drop(columns=['Imagem1', 'Imagem2',
                     'Imagem3', 'Imagem4', 'Imagem5'])

    # Ordenação e estilização...
    data = data[['Data', 'Created By', 'Rede',
                 'Funcao', 'Ruptura', 'Produtos', 'Imagens']]
    data = data.sort_values(by='Data', ascending=False)

    style = """
    <style>
        .dataframe {
            border-collapse: separate;
            border-spacing: 0;
            border: 2px solid #444444;
            border-radius: 15px;
            -moz-border-radius: 15px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
        }
        .dataframe th {
            background-color: #ddd;
            color: black;
            border-bottom: 2px solid #444444;
        }
        .dataframe th, .dataframe td {
            border: none;
            padding: 10px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f3f3f3;
        }
        .dataframe tbody tr:hover {
            background-color: #ddd;
        }
    </style>
    """
    cols_to_hide = ['Produtos', 'Imagens']
    st.markdown(style, unsafe_allow_html=True)
    st.markdown(data.drop(columns=cols_to_hide).to_html(
        index=False, escape=False), unsafe_allow_html=True)

elif chosen_tab == "Visualização de Ruptura":
    def adjusted_treat_product_string(s):
        if not isinstance(s, str):
            return s  # Return the original value if it's not a string
        s = s.replace(';', ',').replace('#', ',')
        if s.startswith(','):
            s = s[1:]
        if s.endswith(','):
            s = s[:-1]
        s = s.replace(',,', ',')
        return s

    def load_and_transform_data():
        # Load the original data
        data = pd.read_csv('sharepoint_data.csv')
        # Convert the 'Data' column to datetime format
        data['Data'] = pd.to_datetime(data['Data'])

        # Apply the adjusted_treat_product_string function to the 'Produtos' column
        data['Produtos'] = data['Produtos'].apply(
            adjusted_treat_product_string)

        # Split the 'Produtos' column by comma and then transform so that each product is on its own row
        data['Produtos'] = data['Produtos'].str.split(',')
        data = data.explode('Produtos', ignore_index=True)

        # Remove leading and trailing spaces from the 'Produtos' column
        data['Produtos'] = data['Produtos'].str.strip()

        return data

    data = load_and_transform_data()

    # Sidebar
    with st.sidebar:
        st.header("Filtros")

        # Date range filter
        min_date = data['Data'].min().date()
        max_date = data['Data'].max().date()
        start_date, end_date = st.date_input(
            "Escolha o intervalo de datas:", [min_date, max_date])

        # Product filter
        unique_products = data['Produtos'].dropna().unique()
        selected_products = st.multiselect(
            "Selecione os produtos:", sorted(unique_products))

        # Rede filter
        unique_redes = data['Rede'].dropna().unique()
        selected_redes = st.multiselect(
            "Selecione as redes:", sorted(unique_redes))

        # Função filter
        unique_funcoes = data['Funcao'].dropna().unique()
        selected_funcoes = st.multiselect(
            "Selecione as funções:", sorted(unique_funcoes))

        # Pessoa filter
        unique_pessoas = data['Created By'].dropna().unique()
        selected_pessoas = st.multiselect(
            "Selecione as pessoas:", sorted(unique_pessoas))

    # Convert the selected date range to datetime for filtering
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Filter data by the selected criteria
    filtered_data = data[(data['Data'] >= start_datetime) & (
        data['Data'] <= end_datetime) & (data['Ruptura'] == 'Yes')]
    if selected_products:
        filtered_data = filtered_data[filtered_data['Produtos'].isin(
            selected_products)]
    if selected_redes:
        filtered_data = filtered_data[filtered_data['Rede'].isin(
            selected_redes)]
    if selected_funcoes:
        filtered_data = filtered_data[filtered_data['Funcao'].isin(
            selected_funcoes)]
    if selected_pessoas:
        filtered_data = filtered_data[filtered_data['Created By'].isin(
            selected_pessoas)]

    # Estilo da tabela
    style = """
    <style>
        .dataframe {
            border-collapse: separate;
            border-spacing: 0;
            border: 2px solid #444444;
            border-radius: 15px;
            -moz-border-radius: 15px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
        }
        .dataframe th {
            background-color: #ddd;
            color: black;
            border-bottom: 2px solid #444444;
        }
        .dataframe th, .dataframe td {
            border: none;
            padding: 10px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f3f3f3;
        }
        .dataframe tbody tr:hover {
            background-color: #ddd;
        }
        .dataframe td {
            white-space: nowrap;  /* Evita que o texto nas células seja quebrado em várias linhas */
            overflow: visible;  /* Exibe todo o texto, mesmo se ele não couber na célula */
            text-overflow: clip;  /* Evita a adição de "..." no final do texto cortado */
        }
    </style>
    """

    columns_to_hide = ['ID', 'Ruptura', 'Created', 'Modified', 'Modified By', 'Imagem1', 'Imagem2',
                       'Imagem3', 'Imagem4', 'Imagem5']
    filtered_data = filtered_data.drop(columns=columns_to_hide)

    localizacao = filtered_data['Localizacao']

    # Descartando a coluna "Localização" do DataFrame
    filtered_data = filtered_data.drop(columns='Localizacao')

    # Adicionando a coluna "Localização" de volta ao DataFrame
    filtered_data['Localização'] = localizacao
    st.markdown(style, unsafe_allow_html=True)

    # Convertendo o DataFrame para uma string HTML
    table_html = filtered_data.to_html(index=False, escape=False)

    # Exibindo a tabela no Streamlit com o estilo aplicado
    st.markdown(table_html, unsafe_allow_html=True)


if chosen_tab == "Visualização de Imagens":
    def adjusted_treat_product_string(s):
        if not isinstance(s, str):
            return s  # Return the original value if it's not a string
        s = s.replace(';', ',').replace('#', ',')
        if s.startswith(','):
            s = s[1:]
        if s.endswith(','):
            s = s[:-1]
        s = s.replace(',,', ',')
        return s

    def load_and_transform_data():
        # Load the original data
        data = pd.read_csv('sharepoint_data.csv')
        # Convert the 'Data' column to datetime format
        data['Data'] = pd.to_datetime(data['Data'])

        # Apply the adjusted_treat_product_string function to the 'Produtos' column
        data['Produtos'] = data['Produtos'].apply(
            adjusted_treat_product_string)

        # Split the 'Produtos' column by comma and then transform so that each product is on its own row
        data['Produtos'] = data['Produtos'].str.split(',')
        data = data.explode('Produtos', ignore_index=True)

        # Remove leading and trailing spaces from the 'Produtos' column
        data['Produtos'] = data['Produtos'].str.strip()

        return data

    data = load_and_transform_data()

    # Sidebar
    with st.sidebar:
        st.header("Filtros")

        # Date range filter
        min_date = data['Data'].min().date()
        max_date = data['Data'].max().date()
        start_date, end_date = st.date_input(
            "Escolha o intervalo de datas:", [min_date, max_date])

        # Product filter
        unique_products = data['Produtos'].dropna().unique()
        selected_products = st.multiselect(
            "Selecione os produtos:", sorted(unique_products))

        # Rede filter
        unique_redes = data['Rede'].dropna().unique()
        selected_redes = st.multiselect(
            "Selecione as redes:", sorted(unique_redes))

        # Função filter
        unique_funcoes = data['Funcao'].dropna().unique()
        selected_funcoes = st.multiselect(
            "Selecione as funções:", sorted(unique_funcoes))

        # Pessoa filter
        unique_pessoas = data['Created By'].dropna().unique()
        selected_pessoas = st.multiselect(
            "Selecione as pessoas:", sorted(unique_pessoas))

    # Convert the selected date range to datetime for filtering
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Filter data by the selected criteria
    filtered_data = data[(data['Data'] >= start_datetime) & (
        data['Data'] <= end_datetime) & (data['Ruptura'] == 'Yes')]
    if selected_products:
        filtered_data = filtered_data[filtered_data['Produtos'].isin(
            selected_products)]
    if selected_redes:
        filtered_data = filtered_data[filtered_data['Rede'].isin(
            selected_redes)]
    if selected_funcoes:
        filtered_data = filtered_data[filtered_data['Funcao'].isin(
            selected_funcoes)]
    if selected_pessoas:
        filtered_data = filtered_data[filtered_data['Created By'].isin(
            selected_pessoas)]

    # Estilo da tabela
    style = """
<style>
    .dataframe {
        border-collapse: collapse;  /* Ajustado para collapse para ter bordas uniformes */
        border: 2px solid #444444;
        border-radius: 15px;
        -moz-border-radius: 15px;
        box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
        table-layout: fixed;
        width: 90%;
        margin: 3px auto;
    }
    .dataframe th {
        background-color: #ddd;
        color: black;
        border: 1px solid #444444;  /* Adiciona bordas às células do cabeçalho */
        font-size: 0.9em;
        text-align: center;
        vertical-align: middle;
        width: 150px;  /* Define uma largura fixa para as células do cabeçalho */
    }
    .dataframe td {
        border: 1px solid #ddd;  /* Adiciona bordas às células de dados */
        padding: 5px;
        font-size: 0.8em;
        text-align: left;
        vertical-align: top;
        white-space: normal;  /* Permite que o texto nas células seja quebrado conforme necessário */
        overflow: hidden;  /* Oculta o conteúdo que excede os limites da célula */
        width: 150px;  /* Define uma largura fixa para as células de dados */
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #f3f3f3;
    }
    .dataframe tbody tr:hover {
        background-color: #ddd;
    }
    img {
        max-width: 80px;
        border-radius: 5px;
    }
</style>
"""

    columns_to_hide = ['ID', 'Ruptura', 'Created', 'Modified', 'Modified By']
    filtered_data = filtered_data.drop(columns=columns_to_hide)

    localizacao = filtered_data['Localizacao']

    # Descartando a coluna "Localização" do DataFrame
    filtered_data = filtered_data.drop(columns='Localizacao')

    # Adicionando a coluna "Localização" de volta ao DataFrame
    filtered_data['Localizacao'] = localizacao

    # Função para criar links HTML das imagens que mostram a imagem diretamente na tabela
    def create_image_link(img):
        if pd.notna(img):
            return f'<a href="{img}" target="_blank"><img src="{img}" style="width:100px;"></a>'
        return ""

    # Aplicando a função para criar os links das imagens para cada coluna de imagem
    for img_col in ['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']:
        filtered_data[img_col] = filtered_data[img_col].apply(
            create_image_link)

    # ...

    # Exibindo a tabela no Streamlit
    st.markdown(style, unsafe_allow_html=True)
    table_html = filtered_data.to_html(index=False, escape=False)
    st.markdown(table_html, unsafe_allow_html=True)
