from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class encode_cat_ruta(BaseEstimator,TransformerMixin):
    '''Clase que permita realizar transformar la variable T.Ruta'''
    def fit(self,X,y=None):
        return self
    def transform(self,X,y=None):
        X=np.where(X=='R.Principal',1,0)
        return X

def escalar_variables(df):
    # separar variables en numericas y categoricas
    df_num=df.select_dtypes(include=np.number).copy()
    df_cat=df.select_dtypes(exclude=np.number).drop(columns=['Cliente','Interlocut','Día']).copy()
    
    # definir atributos
    num_attrib=df_num.columns.tolist()
    cat_attrib=df_cat.columns.tolist()

    # definir pipeline
    full_pipe=ColumnTransformer([('num',StandardScaler(),num_attrib),
                                ('cat',encode_cat_ruta(),cat_attrib)])

    # crear dataframe transformado
    df_tr=pd.DataFrame(full_pipe.fit_transform(df),columns=num_attrib+cat_attrib)

    # concatenar df_cleaned[['Interlocut','Cliente']] con df_tr y retornarlo
    return pd.concat([df[['Día','Interlocut','Cliente']].copy(),df_tr],axis=1)
        
