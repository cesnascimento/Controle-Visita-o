import streamlit as st
import pandas as pd
import datetime
import ast
import re

# Carregar os dados
data = pd.read_csv('testelista2.csv')
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
        options=list(data['Criado por'].unique()),
        key='select_pessoa'
    )

    # Conversão e filtros de data...
    start_date = pd.Timestamp(selected_data[0])
    end_date = pd.Timestamp(selected_data[1])
    data = data[(data['Data'] >= start_date) & (data['Data'] <= end_date)]

    if selected_pessoa:
        data = data[data['Criado por'].isin(selected_pessoa)]
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
    data = data[['Data', 'Criado por', 'Rede',
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
    st.write("Conteúdo da segunda aba")
    st.sidebar.header('Filtros')

    # Filtrar para mostrar apenas os dados onde 'Ruptura' é 'SIM'
    data_ruptura = data[data['Ruptura'] == 'SIM']

    # Modificando a função para criar uma coluna 'Produtos' com listas de produtos
    def explode_products(data):
        # Convertendo a string representando uma lista em uma lista real
        data['Produtos'] = data['Produtos'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        return data

    # Aplicando a modificação na função
    # Aplicando a modificação na função
    data_exploded = explode_products(data_ruptura.copy())

    # Obtendo uma lista exclusiva de produtos
    unique_products = data_exploded['Produtos'].explode().unique().tolist()

    data_exploded = data_exploded.explode('Produtos')

    selected_data = st.sidebar.date_input(
        'Selecione a faixa de datas',
        min_value=data_ruptura['Data'].min().date(),
        max_value=data_ruptura['Data'].max().date(),
        value=(data_ruptura['Data'].min().date(),
               data_ruptura['Data'].max().date()),
        key='select_data'
    )

    selected_produto = st.sidebar.multiselect(
        'Selecione o(s) produto(s)',
        options=unique_products,
        key='select_produto'
    )

    selected_rede = st.sidebar.multiselect(
        'Selecione a(s) rede(s)',
        options=list(data_exploded['Rede'].unique()),
        key='select_rede'
    )
    selected_funcao = st.sidebar.multiselect(
        'Selecione a(s) função(ões)',
        options=list(data_exploded['Funcao'].unique()),
        key='select_funcao'
    )
    selected_pessoa = st.sidebar.multiselect(
        'Selecione a(s) pessoa(s)',
        options=list(data_exploded['Criado por'].unique()),
        key='select_pessoa'
    )

    # Conversão e filtros de data...
    start_date = pd.Timestamp(selected_data[0])
    end_date = pd.Timestamp(selected_data[1])
    data_exploded = data_exploded[(data_exploded['Data'] >= start_date) & (
        data_exploded['Data'] <= end_date)]

# ...
    if selected_produto:
        # Criação de uma coluna booleana
        data_exploded['is_selected_product'] = data_exploded['Produtos'].isin(
            selected_produto)

        # Filtragem com base na coluna booleana
        data_exploded = data_exploded[data_exploded['is_selected_product']]

        # Descartando a coluna booleana
        data_exploded.drop(columns=['is_selected_product'], inplace=True)

    if selected_rede:
        data_exploded = data_exploded[data_exploded['Rede'].isin(
            selected_rede)]
    if selected_funcao:
        data_exploded = data_exploded[data_exploded['Funcao'].isin(
            selected_funcao)]
    if selected_pessoa:
        data_exploded = data_exploded[data_exploded['Criado por'].isin(
            selected_pessoa)]

    # Função para criar links HTML das imagens...
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

    img_url_prefix = "https://dermage.sharepoint.com/sites/AdminHomePage/SiteAssets/Lists/a71446a8-a43c-4fde-ab80-a8440de77d91/"
    data_exploded['Imagens'] = data_exploded.apply(create_image_link, axis=1)
    data_exploded = data_exploded.drop(
        columns=['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5'])

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
    st.markdown(style, unsafe_allow_html=True)

    show_images = st.sidebar.checkbox('Mostrar imagens', value=False)

    # Exibir nome da REDE e tabela para cada grupo de REDE
    for rede, group_data in data_exploded.groupby('Rede'):
        st.markdown(f"## **REDE: {rede}**")
        cols_to_show = ['Data', 'Criado por', 'Rede', 'Funcao', 'Produtos']
        if show_images:
            cols_to_show.append('Imagens')
        st.markdown(group_data[cols_to_show].to_html(
            index=False, escape=False), unsafe_allow_html=True)


if chosen_tab == "Visualização de Imagens":
    st.write("Conteúdo da segunda aba")
    st.sidebar.header('Filtros')

    # Filtrar para mostrar apenas os dados onde 'Ruptura' é 'SIM'
    data_ruptura = data[data['Ruptura'] == 'SIM']

    # Modificando a função para criar uma coluna 'Produtos' com listas de produtos
    def explode_products(data):
        # Convertendo a string representando uma lista em uma lista real
        data['Produtos'] = data['Produtos'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        return data

    # Aplicando a modificação na função
    # Aplicando a modificação na função
    data_exploded = explode_products(data_ruptura.copy())

    # Obtendo uma lista exclusiva de produtos
    unique_products = data_exploded['Produtos'].explode().unique().tolist()

    data_exploded = data_exploded.explode('Produtos')

    selected_data = st.sidebar.date_input(
        'Selecione a faixa de datas',
        min_value=data_ruptura['Data'].min().date(),
        max_value=data_ruptura['Data'].max().date(),
        value=(data_ruptura['Data'].min().date(),
               data_ruptura['Data'].max().date()),
        key='select_data'
    )

    selected_produto = st.sidebar.multiselect(
        'Selecione o(s) produto(s)',
        options=unique_products,
        key='select_produto'
    )

    selected_rede = st.sidebar.multiselect(
        'Selecione a(s) rede(s)',
        options=list(data_exploded['Rede'].unique()),
        key='select_rede'
    )
    selected_funcao = st.sidebar.multiselect(
        'Selecione a(s) função(ões)',
        options=list(data_exploded['Funcao'].unique()),
        key='select_funcao'
    )
    selected_pessoa = st.sidebar.multiselect(
        'Selecione a(s) pessoa(s)',
        options=list(data_exploded['Criado por'].unique()),
        key='select_pessoa'
    )

    # Conversão e filtros de data...
    start_date = pd.Timestamp(selected_data[0])
    end_date = pd.Timestamp(selected_data[1])
    data_exploded = data_exploded[(data_exploded['Data'] >= start_date) & (
        data_exploded['Data'] <= end_date)]

# ...
    if selected_produto:
        # Criação de uma coluna booleana
        data_exploded['is_selected_product'] = data_exploded['Produtos'].isin(
            selected_produto)

        # Filtragem com base na coluna booleana
        data_exploded = data_exploded[data_exploded['is_selected_product']]

        # Descartando a coluna booleana
        data_exploded.drop(columns=['is_selected_product'], inplace=True)

    if selected_rede:
        data_exploded = data_exploded[data_exploded['Rede'].isin(
            selected_rede)]
    if selected_funcao:
        data_exploded = data_exploded[data_exploded['Funcao'].isin(
            selected_funcao)]
    if selected_pessoa:
        data_exploded = data_exploded[data_exploded['Criado por'].isin(
            selected_pessoa)]

    # Função para criar links HTML das imagens...
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

    img_url_prefix = "https://dermage.sharepoint.com/sites/AdminHomePage/SiteAssets/Lists/a71446a8-a43c-4fde-ab80-a8440de77d91/"
    data_exploded['Imagens'] = data_exploded.apply(create_image_link, axis=1)
    data_exploded = data_exploded.drop(
        columns=['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5'])

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
    st.markdown(style, unsafe_allow_html=True)

    show_images = st.sidebar.checkbox('Mostrar imagens', value=True)

    # Exibir nome da REDE e tabela para cada grupo de REDE
    for rede, group_data in data_exploded.groupby('Rede'):
        st.markdown(f"## **REDE: {rede}**")
        cols_to_show = ['Data', 'Criado por', 'Rede', 'Funcao', 'Produtos']
        if show_images:
            cols_to_show.append('Imagens')
        st.markdown(group_data[cols_to_show].to_html(
            index=False, escape=False), unsafe_allow_html=True)
