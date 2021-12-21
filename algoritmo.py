import pandas as pd
import itertools
import pickle

# BASE DE DADOS
data = {
    "leite": [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    "café": [1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    "cerveja": [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "pão": [1, 1, 1, 1, 0, 0, 1, 0, 0, 0],
    "manteiga": [1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
    "arroz": [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    "feijão": [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
}
df = pd.DataFrame(data)

# NÚMERO TOTAL DE REGISTROS
total = df.__len__()

# NOMES DAS COLUNAS
colunas = df.columns.values


# VETOR PARA GUARDAR AS REGRAS DE ASSOCIAÇÃO GERADAS
REGRAS_DE_ASSOCIACAO = []


def get_colunas_y(colunas_x_atuais):
    """
    Função recebe as colunas_X atuais e retorna as colunas y,
    que correspondem as colunas que não estao sendo usadas como X
    :param colunas_x_atuais:
    :return:
    """
    colunas_y = []
    for col in colunas:
        if col not in (colunas_x_atuais):
            colunas_y.append(col)

    return colunas_y


def gera_possibilidades_binarias(quantidade):
    """
    Retorna as possibilidade binarias de compras (SIM E NÃO) de acordo com a quantidade
    de itens presente na coluna X ou Y atual.
    EXEMPLO : LEITE SIM, CAFE SIM / LEITE NÃO CAFE NÃO / LEITE SIM. CAFE NÃO / LEITE NÃO CAFÉ SIM / LEITE
    1,1 / 0,0 / 1,0 / 0,1
    :param quantidade:
    :return:
    """
    resultado = []
    # Gera combinações
    combinacoes = list(itertools.combinations_with_replacement([0, 1], quantidade))
    # Gera permutações dos itens que não são formados pelo mesmo elemento
    for i in range(1, len(combinacoes) - 1):
        resultado.extend(list(set(itertools.permutations(combinacoes[i]))))
    # Adiciona combinação para o primeiro elemento na lista
    resultado.append(combinacoes[0])
    # Adiciona combinação para o ultimo elemento na lista
    resultado.append(combinacoes[len(combinacoes) - 1])
    return resultado


def get_string_regra_x(colums, possibilities):
    """
    Gera o string da regra para o lado X
    :param colums:
    :param possibilities:
    :return:
    """
    regra = ""
    for coluna, possibilidade in zip(colums, possibilities):
        possibilidade = "SIM" if possibilidade == 1 else "NÃO"
        regra += f"SE {coluna} {possibilidade} ,"

    return regra


def get_string_regra_y(colums, possibilities):
    """
    Gera o string da regra para o lado Y
    :param colums:
    :param possibilities:
    :return:
    """
    regra = ""
    for coluna, possibilidade in zip(colums, possibilities):
        possibilidade = "SIM" if possibilidade == 1 else "NÃO"
        regra += f"{coluna} {possibilidade} ,"

    return regra


def get_regras_associacao():
    """
    Gera as regras de associação para o dataset atual.
    :return:
    """

    # Itera sobre a quantidade de itens possíveis para o LADO X, que vai entre 1 e 6, pois são 7 colunas existentes.
    for qtd_itens_x in range(1, len(colunas)):
        # Gera todas as combinações com N elementos, sendo que N depende da quantidade de itens atual
        colunas_x = list(itertools.combinations(colunas, qtd_itens_x))
        # Percorrer cada combinação gerada
        for coluna_x in colunas_x:
            # Para cada combinação atual, que corresponde ao lado X geramos as possibilidade binarias de compras
            # cujo resultado depende da quatidade de itens na coluna atual
            poss_compras_x = gera_possibilidades_binarias(len(coluna_x))
            # Iterar para cada possibilidade de compra para o lado X atual
            for poss_compra_x in poss_compras_x:
                query_x = ""
                # Monta query para consulta no dataframe a quatidade de registros para o X
                for i, x in enumerate(coluna_x):
                    query_x += f"{x} == {poss_compra_x[i]}"
                    if i < len(coluna_x) - 1:
                        query_x += " & "

                num_total_x = len(df.query(query_x))

                # Verifica esse registro, caso contrario, ignora.
                if num_total_x > 0:
                    # Pega as colunas que ainda não estao presentes no lado X, e este sera as possubilidades para o
                    # lado Y
                    colunas_Y = get_colunas_y(coluna_x)
                    # Itera sobre a quantidade de itens possíveis para o LADO Y
                    for qtd_itens_y in range(1, len(colunas_Y)):
                        # Gera todas as combinações com N elementos, sendo que N depende da quantidade de itens atual
                        colunas_y = list(itertools.combinations(colunas_Y, qtd_itens_y))
                        # Percorrer cada combinação gerada
                        for coluna_y in colunas_y:
                            # Para cada combinação atual, que corresponde ao lado Y geramos as possibilidade binarias
                            # de compras cujo resultado depende da quatidade de itens na coluna atual
                            poss_compras_y = gera_possibilidades_binarias(len(coluna_y))
                            for poss_compra_y in poss_compras_y:
                                # Monta query
                                query_y = ""
                                for i, y in enumerate(coluna_y):
                                    query_y += f"{y} == {poss_compra_y[i]}"
                                    if i < len(coluna_y) - 1:
                                        query_y += " & "

                                # Conta os registros com de X e Y que aparecem nas transações dataset
                                new_query = f"{query_x} & {query_y}"
                                num_total_x_y = len(df.query(new_query))

                                # Apenas registra a regras caso num de X e Y seja maior q 0
                                if num_total_x_y > 0:
                                    # Calcula suporte e confiança
                                    confianca = (num_total_x_y / num_total_x)
                                    suporte = (num_total_x / total)

                                    # Registra regral atual
                                    regra_atual = {
                                            "regra": f"{get_string_regra_x(coluna_x, poss_compra_x)} => {get_string_regra_y(coluna_y, poss_compra_y)}",
                                            "suporte": suporte,
                                            "confianca": confianca
                                    }

                                    print(regra_atual)

                                    REGRAS_DE_ASSOCIACAO.append(regra_atual)


def load_regras():
    global REGRAS_DE_ASSOCIACAO
    with open("regras.pickle", "rb") as file:
        REGRAS_DE_ASSOCIACAO = pickle.load(file)


def save_regras():
    pickle_out = open("regras.pickle", "wb")
    pickle.dump(REGRAS_DE_ASSOCIACAO, pickle_out)
    pickle_out.close()


def get_all_regras():
    """
    Pega todas as regras de assoiação geradas.
    :return:
    """
    # get_regras_associacao()
    load_regras()
    for regra in REGRAS_DE_ASSOCIACAO:
        print(f"{regra}\n")

    #save_regras()
    print("Finalizado")


def get_regras_com_suporte_e_confianca_minimo(sup_min, conf_min):
    """
    :return:
    """
    load_regras()
    REGRAS_FILTRADAS = []
    for regra in REGRAS_DE_ASSOCIACAO:
        if regra["suporte"] >= sup_min and regra["confianca"] >= conf_min:
            REGRAS_FILTRADAS.append(regra)
            print(regra)


#get_all_regras()
get_regras_com_suporte_e_confianca_minimo(sup_min=0.6, conf_min=0.6)
