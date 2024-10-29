import  requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
import os
import time
import json

# url base do site
base_url = "https://www.keune.com.br/loja"

# Diretório para salvar dados e imagens
data_directory = 'data'
image_directory = os.path.join(data_directory, 'images')
os.makedirs(image_directory, exist_ok=True)

# Estrutura de dados para salvar informações de produtos

data = {
    "REF": [],
    "Nome do Produto": [],
    "Linha": [],
    "Valor": [],
    "Descrição Geral": [],
    "Código de Barras": [],
    "Modo de Uso": [],
    "Composição": [],
    "Link do Produto": [],
    "Valor promocional": [],
    "Tags": [],
    "Conteúdo da Embalagen": [],
    "Ingredientes Ativos": [],
}

# Seletores de imagens
image_selector = "div.item-image > figure > img" # Percorrer até a trinúltima imagen

# Iterar sobre as páginas
for page in range(1,6):
    url = f"{base_url}?page={page}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Armazenando todos os elementos produtos para percorrer 
        product_elements = soup.select('#wrapper > main > div > div.product-list-content > div.products-wrapper > div > div > a')

        for product_element in product_elements:
            if product_element.has_attr('href'):
                product_link = f"https://www.keune.com.br{product_element['href']}"
                print("Link encontrado:", product_link)

                response_link = requests.get(product_link)
                if response_link.status_code == 200:
                    soup = BeautifulSoup(response_link.text, 'html.parser')
                    
                    # Extraindo informações do produto
                    product_name = soup.select_one('#wrapper > main > div.product-section > div.product-wrap.-container > div.product-infos > div > div > h1').get_text(strip=True)
                    product_name_sanitized = product_name.replace("/", "-") # Para o nome da pasta
                    product_ref = soup.select_one('#wrapper > main > div.product-section > div.product-wrap.-container > div.product-infos > div > div > div.product-reference > span:nth-child(2)').get('data-for')
                    product_price = float(soup.select_one('div.wrapper-price > del').get_text(strip=True).replace("R$ ", "").replace(".", "").replace(",","."))
                    product_description = soup.select_one('div.product-description').get_text(strip=True)
                    
                    # Encontrar todos os parágrafos dentro da div especificada
                    paragraphs = soup.select("div.product-specification > div.text > p")

                    # Inicializar uma variável para guardar todo o texto
                    product_mode = ""

                    # Iterar sobre os parágrafos e adicionar o texto à variável
                    for paragraph in paragraphs:
                        product_mode += paragraph.text + "\n" # Adiciona uma nova linha após cada parágrafo para separação

                    # Encontrar todas as tags <script> com os dados do produto
                    script_tags = soup.find_all('script',type='application/ld+json')

                    found_gtin = False
                    for tag in script_tags:
                        # Tentar carregar o conteúdo JSON dentro da tag <script>
                        try: 
                            data_script = json.loads(tag.string)
                            # Verificar se o JSON é do tipo Produto e contém o campo 'gtin'
                            if data_script['@type'] == 'Product':
                                # Se GTIN estiver diretamente no nível do produto
                                if 'gtin13' in data_script:
                                    product_ean = data_script['gtin13']
                                    found_gtin = True
                                    break
                                # Se GTIN estiver dentro de uma oferta
                                elif 'offers' in data_script:
                                    # Verificar se algum 'offer' contém o campo 'gtin'
                                    if any('gtin' in offer for offer in data_script['offers']):
                                        for offer in data_script['offers']:
                                            if 'gtin' in offer:
                                                product_ean = offer['gtin']
                                                found_gtin = True
                                                break
                                    if found_gtin:
                                        break
                        except json.JSONDecodeError:
                            print('Erro ao decoificar JSON')
                    if not product_ean:
                        product_ean = 0

                    # Tentar encontrar o elemento
                    element = soup.select_one("div.infos-block > div.main-infos > h3 > p")

                    # Usar o operador ternário para atribuir o texto se o elemento for encontrado
                    product_line = element.get_text(strip=True) if element else "any"


                    print(product_line)

                    



                else:
                    print(f"Erro ao carregar a página do link: Status {response_link.status_code}")

            else:
                print("Link não encontrado em um dos produtos")
    
    
    else:
        print(f"Erro ao acessar a página {page}: Status {response.status_code}")