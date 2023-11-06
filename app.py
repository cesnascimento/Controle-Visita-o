import datetime
import streamlit as st
import pandas as pd

# Função para carregar os dados
@st.cache_data
def load_data():
    data = pd.read_csv('sharepoint_data.csv')
    # Convertendo as colunas de data de string para datetime
    data['Data'] = pd.to_datetime(data['Data'], errors='coerce')
    data['Criado'] = pd.to_datetime(data['Criado'], errors='coerce')
    data['Modificado'] = pd.to_datetime(data['Modificado'], errors='coerce')
    data['Produtos'] = data['Produtos'].fillna('Sem produtos')
    data['Produtos'] = data['Produtos'].apply(lambda x: [i.strip() for i in str(x).split(',') if i])
    data['Ruptura'] = data['Ruptura'].replace({'Yes': 'Sim', 'No': 'Não'})
    return data

# Carregar dados
df = load_data()

# Título do painel
st.title('Painel Administrativo de Visita')


# Criar abas
tab1, tab2, tab3 = st.tabs(["Painel Geral", "Painel Ruptura", "Painel Imagens"])

# Filtros (omitidos para brevidade, podem ser adicionados conforme necessidade)
# Filtros para cada coluna especificada
with tab1:
    if 'Localizacao' in df.columns:
        localizacao = st.sidebar.multiselect('Localização:', options=df['Localizacao'].unique())
        if localizacao:
            df = df[df['Localizacao'].isin(localizacao)]

    if 'Rede' in df.columns:
        rede = st.sidebar.multiselect('Rede:', options=df['Rede'].unique())
        if rede:
            df = df[df['Rede'].isin(rede)]

    if 'Funcao' in df.columns:
        funcao = st.sidebar.multiselect('Função:', options=df['Funcao'].unique())
        if funcao:
            df = df[df['Funcao'].isin(funcao)]

    if 'Produtos' in df.columns:
        # Criar uma lista de todos os produtos únicos
        all_products = set()
        for product_list in df['Produtos'].dropna():
            all_products.update(product_list)
        # Usuário pode selecionar produtos individuais
        selected_products = st.sidebar.multiselect('Produtos:', options=sorted(all_products))
        if selected_products:
            # Filtrar linhas que contêm os produtos selecionados
            mask = df['Produtos'].apply(lambda x: any(item for item in selected_products if item in x))
            df = df[mask]

    if 'Criado por' in df.columns:
        criado_por = st.sidebar.multiselect('Criado por:', options=df['Criado por'].unique())
        if criado_por:
            df = df[df['Criado por'].isin(criado_por)]

    # Filtro por intervalo de datas
    if 'Data' in df.columns:
        # Encontrar a data mínima e máxima para definir o range dos datepickers
        min_date = df['Data'].min().date() if df['Data'].min() is not pd.NaT else datetime.now().date()
        max_date = df['Data'].max().date() if df['Data'].max() is not pd.NaT else datetime.now().date()
        # Permitir que o usuário escolha um intervalo de datas
        data_inicial, data_final = st.date_input('Escolha um intervalo de datas:', [min_date, max_date])
        if data_inicial and data_final:
            df = df[(df['Data'].dt.date >= data_inicial) & (df['Data'].dt.date <= data_final)]
    
    if 'Ruptura' in df.columns:
        ruptura = st.multiselect('Ruptura:', options=df['Ruptura'].unique())
        if ruptura:
            df = df[df['Ruptura'].isin(ruptura)]



    # Ocultar colunas específicas
    columns_to_hide = ['ID', 'Criado', 'Modificado', 'Modificado por', 'Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']
    df_display = df.drop(columns=columns_to_hide)

    # Aplicar estilo Bootstrap na tabela
    # Nota: Você pode querer hospedar seu próprio CSS ou usar um CDN diferente
    bootstrap_css = """
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th, .dataframe td {
            border: 1px solid #dddddd;
            padding: 8px;
            text-align: left;
        }
        .dataframe th {
            background-color: #007bff;
            color: white;
        }
    </style>
    """

    # Injeta o CSS do Bootstrap na página
    st.markdown(bootstrap_css, unsafe_allow_html=True)

    # Mostrar dados filtrados com estilo Bootstrap
    st.markdown(df_display.to_html(classes='table table-striped', index=False), unsafe_allow_html=True)
with tab2:
    
    # Filtro de intervalo de datas apenas para esta aba
    data_inicial_tab2, data_final_tab2 = st.date_input('Escolha um intervalo de datas (Ruptura SIM):', [min_date, max_date], key="date_range_ruptura_sim")
    
    # Filtro para Ruptura já aplicado, mostrando apenas "SIM"
    df_ruptura_sim = df[df['Ruptura'] == 'Sim']

    if data_inicial_tab2 and data_final_tab2:
        df_ruptura_sim = df_ruptura_sim[(df_ruptura_sim['Data'].dt.date >= data_inicial_tab2) & (df_ruptura_sim['Data'].dt.date <= data_final_tab2)]

    # Ocultar colunas específicas
    columns_to_hide = ['ID', 'Criado', 'Modificado', 'Modificado por', 'Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']
    df_ruptura_sim_display = df_ruptura_sim.drop(columns=columns_to_hide)

    # Mostrar dados filtrados com estilo Bootstrap
    st.markdown(df_ruptura_sim_display.to_html(classes='table table-striped', index=False), unsafe_allow_html=True)

with tab3:
    # Filtro para mostrar apenas dados com ruptura SIM e com imagens
    df_with_images_and_rupture = df[(df['Ruptura'] == 'Sim') & (df[['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']].notnull().any(axis=1))]
    
    # Função para formatar a coluna de imagem com HTML para exibir a imagem ou um texto alternativo
    def format_image_column(image_url):
        if pd.notnull(image_url):
            return f'<a href="{image_url}" target="_blank"><img src="{image_url}" width="100" /></a>'
        return "Sem foto"
    
    data_inicial_tab3, data_final_tab3 = st.date_input('Escolha um intervalo de datas (Imagens):', [min_date, max_date], key="date_range_ruptura_imagem")
    
    if data_inicial_tab3 and data_final_tab3:
        df_ruptura_sim = df_ruptura_sim[(df_ruptura_sim['Data'].dt.date >= data_inicial_tab2) & (df_with_images_and_rupture['Data'].dt.date <= data_final_tab2)]


    # Aplicar a função de formatação para cada coluna de imagem
    for col in ['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']:
        df_with_images_and_rupture[col] = df_with_images_and_rupture[col].apply(format_image_column)

    columns_to_hide = ['ID', 'Criado', 'Modificado', 'Modificado por']
    df_with_images_and_rupture = df_with_images_and_rupture.drop(columns=columns_to_hide)

    # Mostrar dados filtrados com estilo Bootstrap
    st.markdown(df_with_images_and_rupture.to_html(classes='table table-striped', escape=False, index=False), unsafe_allow_html=True)
# Código para estilo Bootstrap (colocado fora das abas se for comum a ambas)
bootstrap_css = """
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<style>
    .dataframe {
        width: 100%;
        border-collapse: collapse;
    }
    .dataframe th, .dataframe td {
        border: 1px solid #dddddd;
        padding: 8px;
        text-align: left;
    }
    .dataframe th {
        background-color: #007bff;
        color: white;
    }
</style>
"""
st.markdown(bootstrap_css, unsafe_allow_html=True)