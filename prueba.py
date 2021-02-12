import pandas as pd
import numpy as np
from saaty import ahp


def get_attribute_submatrix(attribute, pow_value):
    toret = pd.DataFrame(columns=x.index, index=x.index)
    for index, j in x.iteritems():
        col = [i/j for i in x]
        toret[index] = col
    toret = get_priorities(toret, pow_value)
    return toret

def get_priorities(matrix, pow_value):
    '''
    Normalise matrix given by get_matrix()
    '''
    subm = matrix.pow(pow_value)
    sum_array = [sum(row[1]) for row in subm.iterrows()]
    priorities = [elem/np.sum(sum_array) for elem in sum_array]
    matrix['priorities'] = priorities
    return matrix

df = pd.read_excel('./data/dummy_strat.xlsx')
df.set_index('Alternatives', inplace=True)
df = get_attribute_submatrix(df.econ)
prio = get_priorities(df, 10)


data = pd.read_excel("data/dummy_survey_data.xlsx")
dummy = pd.read_excel("data/dummy_strat.xlsx")
squema = {
        "main":{
            "range":[1,13],
            "attributes":["econ","social","env","coste"]
        },
        "env":{
            "range":[13,19],
            "attributes":["nocons", "zepaozec", "zepayzec"]
        }
    }

    dummy

res = ahp(
  train=True,
  data=data,
  pow_value=10,
  confidence=0.95,
  cratio_threshold=0.1,
  squema=squema
)

res.set_ahp_weights(dummy)