import pandas as pd
import numpy as np

# Função para ler e traduzir os códigos de municípios para nomes e estados
def traducao_municipios():
    
    # Lê o CSV com os municípios (formato "110001:Ro-Alta Floresta D Oeste")
    municipios_raw = pd.read_csv("RAIS_vinculos_layout2020.xls - municipio.csv", header=None, names=["raw"], sep=";")  # ajustar separador se precisar
    
    # Para cada linha do CSV, separa código, estado e nome do município
    municipios_list = []
    for item in municipios_raw["raw"]:
        cod, texto = item.split(":")
        estado, municipio_nome = texto.split("-", 1) 
        municipios_list.append({
            "municpio": int(cod), 
            "estado": estado, 
            "municipio_nome": municipio_nome
        })

    # Cria DataFrame com os municípios tratados
    df_municipios = pd.DataFrame(municipios_list)

    return df_municipios





# Função para ler ocupações, juntar com municípios e dados principais, e limpar o DataFrame   
def traducao_ocupacao(df_municipios):
    
    # Lê CSV com códigos de ocupação
    ocupacao_raw = pd.read_csv("RAIS_vinculos_layout2020.xls - ocupação.csv", header=None, names=["raw"], sep=";") 

    # Para cada linha, separa código da ocupação e nome da ocupação
    ocupacao_list = []
    for item in ocupacao_raw["raw"]:
        cod, ocupacao_nome = item.split(":", 1) 
        ocupacao_list.append({
            "cboocupao2002": int(cod), 
            "ocupacao_nome": ocupacao_nome
        })

    # Cria DataFrame de ocupações
    df_ocupacao = pd.DataFrame(ocupacao_list)

    # Lê o CSV principal com dados dos trabalhadores
    df = pd.read_csv("es2023_limpo.csv", sep=";", dtype={"municpio": int, "cboocupao2002": int,})

    # Faz merge com municípios para adicionar nome e estado
    df = df.merge(df_municipios, on="municpio", how="left")

    # Faz merge com ocupações para adicionar nomes de ocupação
    df = df.merge(df_ocupacao, on="cboocupao2002", how="left")
    
    # Substitui valores vazios por "Ocupação desconhecida"
    df["ocupacao_nome"] = df["ocupacao_nome"].replace(r"^\s*$", np.nan, regex=True)
    df["ocupacao_nome"] = df["ocupacao_nome"].fillna("Ocupação desconhecida")
    
    # Remove colunas que não serão usadas
    df = df.drop(columns=["municpio", "cboocupao2002"])
    
    # Converte idade para Int64
    df['idade'] = df['idade'].astype('Int64')
    
    # Renomeia colunas
    df = df.rename(columns={
        "vlremunmdianom": "remuneracao",
        "idade": "idade_trabalhador",
        "sexotrabalhador": "sexo",
        "escolaridadeaps2005": "escolaridade",
        "ibgesubsetor": "subsetor"
    })
    
    # Converte remuneração para string e substitui pontos por vírgula
    df['remuneracao'] = df['remuneracao'].astype(str).str.replace('.', ',')
    
    # Salva o DataFrame final para usar no Power BI
    df.to_csv("dataframe_limpo.csv", sep=";", index=False, encoding="utf-8-sig")
    print("CSV final salvo como 'dataframe_limpo.csv'")
    
    
    
    
    
# Função principal que executa o fluxo completo
def main():
    df_municipios = traducao_municipios()
    traducao_ocupacao(df_municipios)

if __name__ == "__main__":
    main()
