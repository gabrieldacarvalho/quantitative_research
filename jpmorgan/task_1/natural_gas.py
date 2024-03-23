import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# Carregar os dados
DATA_GAS = pd.read_csv('https://raw.githubusercontent.com/gabrieldacarvalho/quantitative_research/main/jpmorgan/data_base/Nat_Gas.csv')

# Convertendo a coluna 'Dates' para datetime com formato especificado
DATA_GAS['Dates'] = pd.to_datetime(DATA_GAS['Dates'], format='%m/%d/%y')

START_DATE = DATA_GAS['Dates'].min()

# Criando a matriz de variáveis independentes (X) e adicionando a constante
X = sm.add_constant((DATA_GAS['Dates'] - START_DATE).dt.days)

# Variável dependente (y)
Y = DATA_GAS['Prices']

# Ajustando o modelo de regressão linear
MODEL = sm.OLS(Y, X)
FIT1 = MODEL.fit()

# Imprimir o resumo do modelo
print(FIT1.summary())


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


def moving_average(DF, WINDOW_SIZE):
    AVERAGES = []
    N = len(DF)
    # Calculando a média móvel
    for i in range(0, N - WINDOW_SIZE + 1):
        AVERAGES.append(DF['Prices'][i:i + WINDOW_SIZE].mean())

    # Plotando o gráfico da média móvel
    GRAPH1 = px.line(x=DF['Dates'][WINDOW_SIZE - 1:], y=AVERAGES)
    GRAPH1.update_layout(title="Médias Móveis", xaxis_title="Dates")
    GRAPH1.write_html(f"E:/python/Python_Finance/jpmorgan/graph/medias_moveis_h_{WINDOW_SIZE}.html",
                      auto_open=True)


moving_average(DATA_GAS, 12)


# Gráfico séries temporais
FIG1 = px.line(DATA_GAS, x='Dates', y='Prices')

# Adicionar linha de regressão ao gráfico
FIG1.add_trace(go.Scatter(x=DATA_GAS['Dates'], y=FIT1.fittedvalues,
                          mode='lines', name='Linha de Regressão'))

FIG1.write_html("E://python//Python_Finance/jpmorgan//graph//time_series_gas.html",
                auto_open=True)

'''
DATA_INPUT = pd.to_datetime('2024-7-30', format='%Y-%m-%d')
ESTIMATION = price_estimate(DATA_INPUT)
print(f'The estimation of the gas price is {ESTIMATION}')
'''
