import pandas as pd
from collections import defaultdict
import numpy as np
import json
import scipy.stats as st


class ahp():
    '''
    '''
    def __init__(self, train, data, pow_value, confidence, cratio_threshold, squema):
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
                    pow_value = pow_value,
                    cratio_threshold=cratio_threshold
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


    def pipeline(self, df, selection, pow_value, cratio_threshold):
        '''
        '''
        squema = self.build_squema(df, selection)
        weights = defaultdict(list)
        for resp in df.index:
            row = df.loc[resp,]
            matrix = self.get_matrix(squema, selection, row)
            nmatrix = self.get_priorities(matrix, pow_value)
            c_r = self.calculate_consistency_ratio(
                ci=self.calculate_consistency_index(nmatrix),
                cr=self.calculate_random_consistency_index(len(nmatrix.index))
            )
            
            if c_r < cratio_threshold:
                rowweights = self.extract_weights(nmatrix)
                for key in rowweights.keys():
                    weights[key].append(rowweights[key])

        toret = pd.DataFrame(weights)
        return toret
        

    def get_summary_df(self, level):
        '''
        '''
        df = pd.DataFrame()
        for key in self.squema[level].keys():
            if key not in ['range', 'attributes']:
                df[key] = self.squema[level][key]
        return df

    def summary(self, level):
        '''
        '''
        print(self.get_summary_df(level))

    def calculate_consistency_index(self, matrix):
        '''
        '''
        eigen = np.sum(self.get_eigen(matrix))
        n = len(matrix.index)
        ci = (eigen-n)/(n-1)
        return ci

    def get_eigen(self, matrix):
        toret = []
        for i in range(len(matrix.index)):
            if matrix.iloc[:, i].name != 'priorities':
                toret.append(matrix.iloc[:, i].sum()*matrix.iloc[i,:]['priorities'])
        return toret

    def calculate_random_consistency_index(self, n):
        '''
        '''
        cr = {
            1:0,
            2:0,
            3:0.58,
            4:0.9,
            5:1.12,
            6:1.24,
            7:1.32,
            8:1.41,
            9:1.45,
            10:1.49
        }
        return cr.get(n)

    def calculate_consistency_ratio(self, ci, cr):
        '''
        '''
        return ci/cr



def get_submodel(df, path):
    index = pd.read_csv(path, sep=';')
    toret = df[df.REGISTRO.isin(index.respondent)]
    return toret



if __name__ == '__main__':
    with open('./conf/conf.json') as f:
        conf = json.load(f)

    df = pd.read_excel(conf['data_path'])

    model1 = df
    model2 = get_submodel(df, './choice_data/base_data_time.csv')
    model3 = get_submodel(df, './choice_data/dom_data.csv')
    model4 = get_submodel(df, './choice_data/dom_data_time.csv')



    ah = ahp(
        train=conf['train'],
        data=model1,
        pow_value=conf['pow_value'],
        confidence=conf['confidence'],
        cratio_threshold=conf['cratio_threshold'],
        squema=conf['niveles']
    )
    len(ah.weights['main'].index)
    #ah.squema
    df = ah.get_summary_df('main')
    df