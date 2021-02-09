import pandas as pd
from collections import defaultdict
import numpy as np
import scipy.stats as st


class ahp():
    '''
    Class for training AHP weights from survey data and using trained
    weights to perform altenatives ranking.
    '''

    def __init__(self, train, data, pow_value, confidence, cratio_threshold, squema):
        '''
        Constructor. Instanciate the class on survey data to train AHP weights.

        args:
            -train: bool, if true, train new weights on survey data.
            -data: df, data for training the weights.
            -pow_value: int, when calculating priorities, the power to elevate 
                        the matrix. CAUTION: high values in this attribute can 
                        leade to overflow problems.
            -confidence: float, [0,1], confidence degree for IC calculation.
            -cratio_threshold: float, [0,1], threshold to discard inconsistent
                               responses to the survey. Recommended value = 0.1.
            -squema: dict: {
                "name_of_the_level": {
                    "range": list, [fcolum, lcolum], index of the first and last
                             column from survey data df in which can be found the 
                             data of this level.
                    "attributes": list, attribute names of this level. if there is 
                                  a sublevel, them the sublevel key must be the same
                                  as the name of the attribute in this list. 
                }
            }

        '''
        self.data = data
        self.squema = squema
        self.weights = {}
        if train:
            for level in squema.keys():
                self.weights[level] = self.pipeline(
                    df=self.data,
                    selection=self.get_selection_from_squema(level),
                    pow_value=pow_value,
                    cratio_threshold=cratio_threshold
                )
                self.append_weights_mean(level=level)
                self.append_weights_std(level=level)
                self.append_weights_ic(level=level, confidence=confidence)

        else:
            pass

    def append_weights_mean(self, level):
        '''
        Add new column with weights_mean.

        args:
            -level: string, level to be appended.
        '''
        self.squema[level]['weights_mean'] = self.weights[level].apply(
            np.mean, axis=0
        )

    def append_weights_std(self, level):
        '''
        Add new column with weights_std.

        args:
            -level: string, level to be appended.
        '''
        self.squema[level]['weights_std'] = self.weights[level].apply(
            np.std, axis=0
        )

    def append_weights_ic(self, level, confidence=0.95):
        '''
        Add new column with weights_IC.

        args:
            -level: string, level to be appended.
            -confidence: float, [0,1], confidence degree for IC calculation.
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
        Return interable with selection indexes.
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
        toret[toret.columns == toret.index] = 1
        return(toret)

    def get_matrix(self, squema, selection, row):
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
                    squema.loc[fattribute, sattribute] = value
                    squema.loc[sattribute, fattribute] = 1/value
                if selection == 2:
                    squema.loc[fattribute, sattribute] = 1/value
                    squema.loc[sattribute, fattribute] = value
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
            row = df.loc[resp, ]
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

    def get_summary_list(self):
        '''
        Return dict with summary statistics of calculated weights from 
        survey data.

        '''
        toret = {}
        for level in self.squema.keys():
            df = pd.DataFrame()
            for key in self.squema[level].keys():
                if key not in ['range', 'attributes']:
                    df[key] = self.squema[level][key]
            toret[level] = df
        return toret

    def calculate_consistency_index(self, matrix):
        '''
        Return consistency index Saaty measure from an 
        AHP ranking matrix.

        args:
            -matrix: pd.DataFrame, matrix from wich calculate
                     the consistency index.
        '''
        eigen = np.sum(self.get_eigen(matrix))
        n = len(matrix.index)
        ci = (eigen-n)/(n-1)
        return ci

    def get_eigen(self, matrix):
        '''
        Return eigen values list from a matrix.

        args:
            -matrix: pd.DataFrame, matrix from wich calculate
                     eigenvalues.
        '''
        toret = []
        for i in range(len(matrix.index)):
            if matrix.iloc[:, i].name != 'priorities':
                toret.append(matrix.iloc[:, i].sum()
                             * matrix.iloc[i, :]['priorities'])
        return toret

    def calculate_random_consistency_index(self, n):
        '''
        Return radom consistency index from precalculated values.

        args:
            -n: int, number of rows of the ranking matrix.
        '''
        cr = {
            1: 0,
            2: 0,
            3: 0.58,
            4: 0.9,
            5: 1.12,
            6: 1.24,
            7: 1.32,
            8: 1.41,
            9: 1.45,
            10: 1.49
        }
        return cr.get(n)

    def calculate_consistency_ratio(self, ci, cr):
        '''
        Return consistency ratio as a ratio of consistency index and
        random consistency index.

        args:
            -ci: float, consistency index.
            -cr: float, random consistency index.
        '''
        return ci/cr

    def set_ahp_weights(self, data):
        '''
        Return scaled data with calculated weights for ahp ranking.

        args:
            -data: df, data for which has to be calculated the ranking.
        '''
        data.set_index('Alternatives', inplace=True)
        data = data.apply(self.refactor, axis=0)

        for key in self.squema.keys():
            if key != 'main':
                df = data[self.squema[key]['attributes']]
                df = self.get_weights(key, df, self.squema)
                data[key] = df['weight']

        toret = self.get_weights('main', data, self.squema)
        return toret

    def get_weights(self, key, data, squema):
        '''
        Returns calculated weights on data for a given sublevel
        from the general ahp squema.

        args:
            -key: string, name of the attribute sublevel. if "main" ,
                  them it is the root level in the ahp hierarchy.
            -data: df, data for which has to be calculated the ranking.
            -squema: pretrained squema from ahp class.
        '''
        weights = squema[key]['weights_mean']
        for index, row in data.iterrows():
            w = 0
            for i in weights.index:
                w = w + weights.loc[i] * row[i]

            data.at[index, 'weight'] = w
        return data

    def rescale(self, x, lower=0, upper=1):
        '''
        Returns a reescalated variable.

        args:
            -x: list, array to be reescalated.
            -lower: float, lower bound of the reescalation.
            -upper:float. upper bound of the reescalation.
        '''
        xmin = np.min(x)
        xmax = np.max(x)
        factor = (upper - lower) / (xmax - xmin)
        return ((x - xmin) * factor + lower)

    def refactor(self, x):
        '''
        Returns a refactorized variable as proportion of 1.

        args:
            -x: list, array to be refactorized.
        '''
        return x/np.sum(x)