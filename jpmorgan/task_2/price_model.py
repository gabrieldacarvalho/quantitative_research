# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 12:17:49 2024

@author: gabriel_carvalho

Ótimo trabalho! A mesa agora tem os dados de preço de que precisa. 
O ingrediente final antes que eles possam começar a negociar com o cliente é o 
modelo de preços. Alex diz que o cliente quer começar a negociar o mais rápido
possível. Eles acreditam que o inverno será mais frio do que o esperado, então 
eles querem comprar gás agora para armazenar e vender no inverno, a fim de
aproveitar o aumento resultante nos preços do gás. Eles pedem que você escreva
um script que eles possam usar para precificar o contrato. Quando a mesa estiver 
satisfeita, você trabalhará com engenharia, risco e validação de modelo para 
incorporar esse modelo ao código de produção.

O conceito é simples: qualquer acordo comercial é tão valioso quanto o preço 
que você pode vender menos o preço pelo qual você é capaz de comprar. Qualquer
custo incorrido como parte da execução deste contrato também é deduzido do 
valor global. Então, por exemplo, se eu puder comprar um milhão de MMBtu de
gás natural no verão a US$ 2/MMBtu, armazenar isso por quatro meses e garantir 
que posso vender a mesma quantidade a US$ 3/MMBtu sem incorrer em custos 
adicionais, o valor desse contrato seria de US$ 3-US$ 2) *1e6 = US$ 1 milhão. 
Se houver custos envolvidos, como ter que pagar ao proprietário da instalação 
de armazenamento uma taxa fixa de US $ 100 mil por mês, então o "valor" do 
contrato, na minha perspectiva, cairia no valor total do aluguel para US $ 600 mil. 
Outro custo pode ser o custo de injeção/retirada, como ter que pagar ao 
proprietário da instalação de armazenamento US $ 10 mil por 1 milhão de MMBtu 
para injeção/retirada, então o preço cairá ainda mais em US $ 10 mil para 
US $ 590 mil. Além disso, se eu deveria pagar uma conta de US $ 50 mil cada 
vez para transportar o gás de e para a instalação, o custo deste contrato 
cairia em mais US $ 100 mil. Pense na avaliação como uma estimativa justa na 
qual tanto a mesa de operações quanto o cliente ficariam felizes em celebrar o 
contrato.
"""

import pandas as pd
import statsmodels.api as sm
from tabulate import tabulate


def price_estimate(DATA):
    """
        This function estimates the future price of natural gas based on a regression model.
    Parameters:
    DATA (pd.Timestamp): The date for which the price is to be estimated.

    Returns:
    float: The estimated price of natural gas.

    """
    DAY = (DATA - START_DATE).days
    X0 = [1, DAY]
    PREDICTION = FIT1.predict(X0)
    return PREDICTION[0]


def function_price_model(DF):
    # Convertendo as datas de entrada e saída para o formato das datas no DataFrame
    # pd.to_datetime(DATE_OUT)
    COSTS_VALUE = {
        "Armazenation": [0],
        "Rate Withdrawal": [0],
        "Transport": [0],
    }
    BUY_TABLE = {"Date": [], "Quantity": [], "Value Gas": []}
    SELL_TABLE = {"Date": [], "Quantity": [], "Value Gas": []}
    N_DATEI = int(input("How many injections date? "))
    N_DATEO = int(input("How many withdrawal date? "))
    for i in range(0, N_DATEI):
        BUY_TABLE["Date"].append(
            pd.to_datetime(input("Input injection date [m/d/y]: "))
        )
        if BUY_TABLE["Date"][i] not in DATA["Dates"].values:
            BUY_TABLE["Value Gas"].append(price_estimate(BUY_TABLE["Date"][i]))
        else:
            BUY_TABLE["Value Gas"].append(
                DATA.loc[
                    DATA["Dates"] == BUY_TABLE["Date"][i], "Prices"
                ].values[0]
            )
    CONT = 0
    while True:
        print(
            f"More {1000000 - sum(BUY_TABLE['Quantity'])} gas can be purchased"
        )
        BUY_TABLE["Quantity"].append(
            int(
                input(
                    (
                        f"1.{CONT+1}) Amount of gas to be purchased in "
                        f"{BUY_TABLE['Date'][CONT]} by {BUY_TABLE['Value Gas'][CONT]}? "
                    )
                )
            )
        )

        if sum(BUY_TABLE["Quantity"]) > 10**6:
            BUY_TABLE["Quantity"].pop()
            print(
                "\033[91mThe total amount exceeds 1,000,000. Please enter again.\033[0m"
            )
            continue
        CONT += 1
        if sum(BUY_TABLE["Quantity"]) == 10**6 or CONT == N_DATEI:
            break
    for o in range(0, N_DATEO):
        SELL_TABLE["Date"].append(
            pd.to_datetime(input("Input withdrawal date [m/d/y]: "))
        )
        if SELL_TABLE["Date"][o] in DATA["Dates"].values:
            SELL_TABLE["Value Gas"].append(
                DATA.loc[
                    DATA["Dates"] == SELL_TABLE["Date"][o], "Prices"
                ].values[0]
            )
        else:
            SELL_TABLE["Value Gas"].append(
                price_estimate(SELL_TABLE["Date"][o])
            )
    CONT = 0
    while True:
        print(
            f"More {sum(BUY_TABLE['Quantity']) - sum(SELL_TABLE['Quantity'])} gas can be withdrawal"
        )
        SELL_TABLE["Quantity"].append(
            (
                int(
                    input(
                        f"2.{CONT+1}) How much do you want to withdraw in {SELL_TABLE['Date'][CONT]} "
                        f"by {SELL_TABLE['Value Gas'][CONT]:.2f}? "
                    )
                )
            )
        )

        if sum(SELL_TABLE["Quantity"]) > sum(BUY_TABLE["Quantity"]):
            SELL_TABLE["Quantity"].pop()
            print(
                f"\033[91mThe total amount exceeds {sum(BUY_TABLE['Quantity'])}. Please enter again.\033[0m"
            )
            continue
        CONT += 1
        if CONT == N_DATEO:
            SELL_TABLE["Quantity"][
                SELL_TABLE["Value Gas"].index(min(SELL_TABLE["Value Gas"]))
            ] += sum(BUY_TABLE["Quantity"]) - sum(SELL_TABLE["Quantity"])
            break
    # print(PRICE_OUT)
    print("\033[93mTHE MAX QUANTITY THE GAS IS 1.000.000\033[0m")
    COSTS_VALUE["Transport"][0] += (5 * 10**4) * (
        len(BUY_TABLE["Date"]) + len(SELL_TABLE["Date"])
    )
    COSTS_VALUE["Rate Withdrawal"][0] += sum(BUY_TABLE["Quantity"]) * (
        10**4 / 10**6
    )
    COSTS_VALUE["Armazenation"][0] += (
        (max(SELL_TABLE["Date"]).year - min(BUY_TABLE["Date"]).year) * 12
    ) + (max(SELL_TABLE["Date"]).month - min(BUY_TABLE["Date"]).month)
    print("\n #INJECTION TABLE:")
    print(tabulate(BUY_TABLE, headers="keys", tablefmt="fancy_grid"))
    print("\n #WITHDRAWAL TABLE:")
    print(tabulate(SELL_TABLE, headers="keys", tablefmt="fancy_grid"))
    print("\n #COSTS TABLE:")
    print(tabulate(COSTS_VALUE, headers="keys", tablefmt="fancy_grid"))
    VALUE_OPERATION = sum(SELL_TABLE["Quantity"]) * sum(
        SELL_TABLE["Value Gas"]
    ) - (
        sum(COSTS_VALUE["Armazenation"])
        + sum(COSTS_VALUE["Rate Withdrawal"])
        + sum(COSTS_VALUE["Transport"])
        + sum(BUY_TABLE["Quantity"]) * sum(BUY_TABLE["Value Gas"])
    )
    print("\n #FINAL VALUE OF THE OPERATION:")
    return VALUE_OPERATION


DATA = pd.read_csv(
    "https://raw.githubusercontent.com/gabrieldacarvalho/quantitative_research/main/jpmorgan/data_base/Nat_Gas.csv",
    parse_dates=["Dates"],
)

START_DATE = DATA["Dates"].min()

# Criando a matriz de variáveis independentes (X) e adicionana constante
X = sm.add_constant((DATA["Dates"] - START_DATE).dt.days)

# Variável dependente (y)
Y = DATA["Prices"]

# Ajustando o modelo de regressão linear
MODEL = sm.OLS(Y, X)
FIT1 = MODEL.fit()


function_price_model(DATA)
# function_price_model(DATA, ["10/31/20", "11/30/20"], "10/31/24")
