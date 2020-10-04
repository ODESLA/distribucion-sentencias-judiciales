# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This is a boilerplate pipeline 'prob_func'
generated using Kedro 0.16.2
"""

import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from scipy.interpolate import griddata

def filtrado_conteo(data):
    """Nodo para filtar y contar la cantidad de causas por juzgado.
    Los estados posibles son: 'ASIGNADO', 'ARCHIVADO', 'EN VISTA', 'PASE', 
    'CERRADO','EN DESPACHO', 'ANULADO', 'INICIAL', 'MIGRACION', 'PRINCIPAL',
    'RESUELTO', 'EN TRAMITE', 'RADICADO', 'REMITIDO POR INCOMPETENCIA',
    'PREARCHIVO'.
    Retorna un dataframe con dos columnas, identificando el juzgado y el numero
    de causas activas correspondientes.
    """
    # Filtro para obtener solo causas activas. ToDo: revisar que categorias se consideran activas.
    df = data[(data["est_descr"] == 'INICIAL') | (data["est_descr"] == 'EN VISTA')]

    # Serie con la cantidad de causas por juzgado
    counts = df["org_cod_pri"].value_counts()
    
    # Empaqueto todo en un DataFrame y lo mezclo 
    df = shuffle(pd.DataFrame({'Juzgado': counts.index, 'Causas': counts.values}))

    #Reseteo el index
    df = df.reset_index(drop= True)

    return df


def calculo_probabilidad(data, alfa):
    """Nodo para generar la distribucion de probabilidad.
    Recibe un DataFrame y un valor alfa. El valor alfa funciona como parametro
    de la velocidad de convergencia.
    Devuelve el DataFrame original mas la columna de probabilida y columna "X".
    """
                 
    df = data.copy()
    causas = data["Causas"]
    njuz = len(causas)  
    
    # Probabilidad a asignar a cada juzgado
    P = 1.0/(causas-np.min(causas)+alfa)
    
    # Normalizacion 
    P = P/np.sum(P)
    
    # Genera función para transformar de función uniforme a la que queremos
    X=np.zeros(njuz)
    X[0]= P[0]
    for ii in range(njuz-1):
        X[ii+1] = P[ii] + X[ii]
        
    # Empaquetamos todo en un DataFrame
    df["Probabilidad"] = P
    df["X"] = X
    
    return df


def sorteo(data):

    X = data["X"]
    Y = data.index

    # Valor aleatorio para la interpolacion.
    s = np.random.uniform(0,1)

    juz_sorteado = np.int(griddata(X, Y, s, method='linear'))
    
    juz_sorteado = data.loc[juz_sorteado]["Juzgado"]

    print("***")
    print("El juzgado sorteado es el {}.".format(juz_sorteado))
    print("***")