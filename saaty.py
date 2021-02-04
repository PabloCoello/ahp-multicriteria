import pandas as pd
from collections import defaultdict
import numpy as np
import json
import scipy.stats as st


class ahp():
    '''
    '''
    def __init__(self, train, data, pow_value, confidence, squema):
        '''
        '''
        self.data = data
        self.squema = squema
        self.weights = {}
        if train:
            for level in squema.keys():
                self.weights[level] = self.pipeline(
                    df = self.data,
                    selection = self.get_selection_from_squema(level),
                    pow_value = pow_value
                )
                self.append_weights_mean(level=level)
                self.append_weights_std(level=level)
                self.append_weights_ic(level=level, confidence=confidence)
                
        else:
            pass

    def append_weights_mean(self, level):
        '''
        '''
        self.squema[level]['weights_mean'] = self.weights[level].apply(
            np.mean, axis=0
        )

    def append_weights_std(self, level):
        '''
        '''
        self.squema[level]['weights_std'] = self.weights[level].apply(
            np.std, axis=0
        )

    def append_weights_ic(self, level, confidence=0.95):
        '''
        '''
        def mean_confidence_interval(column, confidence):
            '''
            '''
            a = 1.0 * np.array(column)
            n = len(a)
            m, se = np.mean(a), st.sem(a)
            h = se * st.t.ppf((1 + confidence) / 2., n-1)
            return m-h, m+h
        self.squema[level]['weights_IC_'+str(confidence)] = self.weights[level].apply(
            mean_confidence_interval, confidence=confidence, axis=0
        )

    
    def get_selection_from_squema(self, level):
        '''
        '''
        selection = range(
            self.squema[level]['range'][0],
            self.squema[level]['range'][1]
        )
        return selection


    def build_squema(self, df, selection):
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


    def get_matrix(self, squema,selection, row):
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


    def get_priorities(self, matrix, pow_value):
        '''
        Normalise matrix given by get_matrix()
        '''
        subm = matrix.pow(pow_value)
        sum_array = [sum(row[1]) for row in subm.iterrows()]
        priorities = [elem/np.sum(sum_array) for elem in sum_array]
        matrix['priorities'] = priorities
        return matrix


    def extract_weights(self, nmatrix):
        '''
        Return multicriteria  weights as mean of normalised matrix values.
        '''
        toret = {}
        for row in nmatrix.index:
            toret[row] = nmatrix.loc[row, ]['priorities']
        return toret


    def pipeline(self, df, selection, pow_value):
        '''
        '''
        squema = self.build_squema(df, selection)
        weights = defaultdict(list)
        for resp in df.index:
            row = df.loc[resp,]
            matrix = self.get_matrix(squema, selection, row)
            nmatrix = self.get_priorities(matrix, pow_value)
            rowweights = self.extract_weights(nmatrix)
            for key in rowweights.keys():
                weights[key].append(rowweights[key])

        toret = pd.DataFrame(weights)
        return toret


if __name__ == '__main__':
    with open('./conf/conf.json') as f:
        conf = json.load(f)

    ah = ahp(
        train=conf['train'],
        data=pd.read_excel(conf['data_path']),
        pow_value=conf['pow_value'],
        confidence=conf['confidence'],
        squema=conf['niveles']
    )
    ah.squema