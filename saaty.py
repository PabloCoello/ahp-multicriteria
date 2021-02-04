import pandas as pd
from collections import defaultdict
import numpy as np

def build_squema(df, selection):
    '''
    Returns matrix squema.
    '''
    names = []
    for name in df.columns[selection]:
        split = name.split('_')
        if len(split) == 3:
            if split[1] not in names:
                names.append(split[1])
            if split[2] not in names:
                names.append(split[2])
    toret = pd.DataFrame(
        columns=names,
        index=names
    )
    toret[toret.columns==toret.index] = 1
    return(toret)


def get_matrix(squema,selection, row):
    '''
    First step of the extraction of multicriteria weights, returns matrix of
    scores based on saaty scale.
    '''
    row = row.iloc[selection]
    for i in row.index:
        info = i.split('_')
        if info[1] != 'resp':
            selection = row[i]
            fattribute = info[1]
            sattribute = info[2]
        else:
            value = row[i]
            if selection == 1:
                squema.loc[fattribute,sattribute] = value
                squema.loc[sattribute,fattribute] = 1/value
            if selection == 2:
                squema.loc[fattribute,sattribute] = 1/value
                squema.loc[sattribute,fattribute] = value
    return squema


def get_priorities(matrix, pow_value):
    '''
    Normalise matrix given by get_matrix()
    '''
    subm = matrix.pow(pow_value)
    sum_array = [sum(row[1]) for row in subm.iterrows()]
    priorities = [elem/np.sum(sum_array) for elem in sum_array]
    matrix['priorities'] = priorities
    return matrix


def extract_weights(nmatrix):
    '''
    Return multicriteria  weights as mean of normalised matrix values.
    '''
    toret = {}
    for row in nmatrix.index:
        toret[row] = nmatrix.loc[row, ]['priorities']
    return toret

def pipeline(df, selection):
    squema = build_squema(df, selection)
    weights = defaultdict(list)
    for resp in df.index:
        row = df.loc[resp,]
        matrix = get_matrix(squema, selection, row)
        nmatrix = get_priorities(matrix, 10)
        rowweights = extract_weights(nmatrix)
        for key in rowweights.keys():
            weights[key].append(rowweights[key])

    toret = pd.DataFrame(weights)
    return toret


df = pd.read_excel('./data/Datos.xlsx')
df

nmatrix = get_priorities(matrix, 10)

nenv = range(13,19)
nmain = range(1, 13)
selection = nmain

weights = pipeline(df, nenv)
env_weights = weights.apply(np.mean, axis=0)

weights = pipeline(df, nmain)
main_weights = weights.apply(np.mean, axis=0)
env_weights
main_weightsdx

matrix

