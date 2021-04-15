import pandas as pd
import numpy as np
from saaty import ahp



data = pd.read_excel("data/dummy_survey_data.xlsx")
dummy = pd.read_excel("data/dummy_asneves.xlsx")
squema = {
        "main":{
            "range":[1,13],
            "attributes":["econ","social","env","coste"]
        }
    }

res = ahp(
  train=True,
  data=data,
  pow_value=10,
  confidence=0.95,
  cratio_threshold=1,
  squema=squema
)
res.squema
res.weights
res.cr.hist()
res.weights['main'].coste.hist()

res.get_summary_list()
df = res.set_ahp_weights(dummy, inverse = ['coste'])

serie = df['coste'].sort_values(ascending=True)
val = serie.sort_values(ascending=False).values
for row, index in zip(serie.iteritems(),range(len(serie))):
  serie.at[row[0]] = val[index]
df['coste'] = serie

1-df['coste']
res.priorities_matrix
pairwise = res.attribute_pairwise_matrix
pairwise['econ']
pairwise['env']
pairwise['social']
pairwise['econ']