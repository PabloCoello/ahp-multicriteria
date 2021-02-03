import pandas as pd
import json

class ahp:
    '''
    Computes ahp based on Scholl et.al. 2004
    '''
    def __init__(self, criteria, lvls, hierarchy):
        '''
        '''
    
    
if __name__ == '__main__':
    with open('./conf/multicriteria_conf.json') as f:
        conf = json.load(f)
        
    hierarchy = conf['niveles']
    criteria = pd.read_csv('./data/criterios.csv', sep=';', index_col=0)
    lvls = pd.read_csv('./data/grados.csv', sep=';', index_col=0)    
        