from shareplum import Site
from shareplum import Office365
import csv
import json
from datetime import datetime

# Função para tratar a string da coluna "Produtos"
def treat_product_string(s):
    s = s.replace(';', ',').replace('#', ',')
    if s.startswith(','):
        s = s[2:]
    if s.endswith(','):
        s = s[:-2]
    s = s.replace(',,', ',')
    return s

# Função para tratar a coluna de imagem
def treat_image_column(value):
    try:
        image_data = json.loads(value)
        if 'serverUrl' in image_data and 'serverRelativeUrl' in image_data:
            return image_data['serverUrl'] + image_data['serverRelativeUrl']
    except:
        pass
    return value

# Função atualizada para tratar a coluna "Data"
def updated_treat_date_column(date_value):
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y/%m/%d')
    elif isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        except:
            pass
    return date_value

# Autenticar e conectar ao SharePoint
authcookie = Office365('https://dermage.sharepoint.com', username='cnascimento@dermage.com.br', password='039579X').GetCookies()
site = Site('https://dermage.sharepoint.com/sites/AdminHomePage', authcookie=authcookie)

# Obter dados da lista SharePoint
sp_list = site.List('testelista2')
data = sp_list.GetListItems()

# Mapeamento das colunas antigas para as novas
column_mapping = {
    'Created': 'Criado',
    'Created By': 'Criado por',
    'Modified': 'Modificado',
    'Modified By': 'Modificado por'
}

# Definir as colunas desejadas com os novos nomes
columns_to_keep = [
    'ID', 'Localizacao', 'Rede', 'Funcao', 'Ruptura', 'Produtos',
    'Criado', 'Criado por', 'Modificado', 'Modificado por', 'Data',
    'Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5'
]

filtered_data = []
for row in data:
    # Renomeando as colunas
    for old_name, new_name in column_mapping.items():
        if old_name in row:
            row[new_name] = row.pop(old_name)
    if 'Produtos' in row:
        row['Produtos'] = treat_product_string(row['Produtos'])
    for image_col in ['Imagem1', 'Imagem2', 'Imagem3', 'Imagem4', 'Imagem5']:
        if image_col in row:
            row[image_col] = treat_image_column(row[image_col])
    if 'REDE2' in row:
        row['Rede'] = row.pop('REDE2')
    if 'Data' in row and row['Data']:
        row['Data'] = updated_treat_date_column(row['Data'])
    filtered_row = {k: row.get(k, None) for k in columns_to_keep}
    filtered_data.append(filtered_row)

# Escrever os dados em um arquivo CSV
with open('sharepoint_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=columns_to_keep)
    writer.writeheader()
    for row in filtered_data:
        writer.writerow(row)

print("Dados salvos em sharepoint_data.csv!")
