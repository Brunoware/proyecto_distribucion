# importar funciones
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from docplex.mp.model import Model

def ordenar_arcos_activos(arcos):
    # definir lista para arcos activos ordenados
    arcos_activos_ord=list()
    
    # obtener el primer punto en los arcos
    for i,j in arcos:
        if i==0:
            first_point=(i,j)
            break
    # agregar los puntos con .extend
    arcos_activos_ord.extend([first_point[0],first_point[1]])
    
    # pasar los arcos a listas
    flag_activos=list(arcos)
    
    # remover el punto inicial
    flag_activos.remove(first_point)
    
    # el punto a alcanzar es el primero j de (i,j)
    point_to_search=first_point[1]
    
    # obtener el punto j de (i,j) para establecer el consecutivo
    # por ejemplo en la lista con el primer punto removido (0,1): [(1,2),(4,3),(2,6),(6,5),(5,4)]
    # el primer search seria el j=1 del primer punto, luego en el interador de n=len([(1,2),(4,3),(2,6),(6,5),(5,4)])
    # se busca el i que sea igual a j para obtner el nuevo j y este sea el punto a buscar en el siguiente i del siguiente punto
    # en el ejemplo seguiría buscar un i=1 para el previo j=1, este punto encontrado es (1,2) donde el nuevo i=1 y el punto
    # nuevo a buscar j es 2, y este sería el nuevo i para para el siguiente, el cual es (2,6) y así sucesivamente
    for _ in range(len(flag_activos)):
        for i,j in flag_activos:
            if point_to_search==i:
                point_to_search=j
                arcos_activos_ord.append(j)
                break
    
    return arcos_activos_ord
    
def ruteo_dinamico(df,capacidad_camion):
    # definir datos de clientes
    n_clientes=len(df)
    clientes=list(range(1,n_clientes+1))
    nodos=[0]+clientes# puntos de los clientes más el nodo 0 que es el centro
    Q=capacidad_camion # capacidad de vehículos
    q=dict(zip(clientes,df.Real.tolist()))# capacidad de clientes
    
    # definir coordenadas
    centro=(-12.066883514538135, -76.97871779045312) # planta ATE
    coor_lat=np.insert(df.Latitud.values,0,centro[0],axis=0)# coordenadas de los puntos de venta + planta ATE
    coor_lon=np.insert(df.Longitud.values,0,centro[1],axis=0)
    
    # crear estructura de datos
    arcos={(i,j) for i in nodos for j in nodos if i!=j}
    distancia={(i,j):np.hypot(coor_lat[i]-coor_lat[j],coor_lon[i]-coor_lon[j]) for i in nodos for j in nodos if i!=j}
    
    # creación y optimización - CVRP
    mdl=Model('CVRP')
    
    # creando variables de decisión
    x=mdl.binary_var_dict(arcos,name='x')
    u=mdl.continuous_var_dict(nodos,ub=Q,name='u')
    
    # función objetivo: la menor ruta, minimizar
    mdl.minimize(mdl.sum(distancia[i,j]*x[i,j] for i,j in arcos))
    
    # establecer restricciones
    mdl.add_constraints(mdl.sum(x[i,j] for j in nodos if i!=j)==1 for i in clientes)# no se puede ir a varios nodos desde uno
    mdl.add_constraints(mdl.sum(x[i,j] for i in nodos if i!=j)==1 for j in clientes)
    mdl.add_indicator_constraints(mdl.indicator_constraint(x[i,j],u[i]+q[j]==u[j]) for i,j in arcos if i!=0 and j!=0)
    mdl.add_constraints(u[i]>=q[i]for i in clientes)
    
    # obtener la solución
    mdl.parameters.timelimit=120
    solucion=mdl.solve()
    
    # obtener los arcos donde se establece la ruta
    arcos_activos=[k for k in arcos if x[k].solution_value>0.9]
    
    # validar si estan ordenados
    arcos_activos_sorted=ordenar_arcos_activos(arcos_activos)
    
    # retornar estado de la solución y los arcos
    return mdl.get_solve_status(),arcos_activos,arcos_activos_sorted

def plot_mejor_ruta(lat,lon,arcos_sorted,n_cluster,zoom=5):
    # crear diccionario de colores
    colors=['#8B8378','#00FFFF','#76EEC6','#838B8B','#E3CF57','#0000FF','#00008B','#8A2BE2','#9C661F','#FF4040',
    '#98F5FF','#FF6103','#7FFF00','#DC143C','#68228B','#C1FFC1','#00BFFF','#FF1493','#ADFF2F','#191970',
    '#FF8247','#800000','#FFE4E1']
    n_clusters=range(0,23)
    dic_colors=dict(zip(n_clusters,colors))
    
    # centros para iniciar el mapa
    lat_center = lat.mean()
    lon_center = lon.mean()
    
    # inicializar figura
    fig=go.Figure()
    
    # ordenar coordenadas
    lat_sorted=[lat[i] for i in arcos_sorted]
    lon_sorted=[lon[i] for i in arcos_sorted]
    
    # agregar coordenadas de cluster
    fig.add_trace(go.Scattermapbox(
            name = f'Cluster N° {n_cluster}',
            lon = lon_sorted,
            lat = lat_sorted,
            mode="markers+lines+text",
            marker =go.scattermapbox.Marker(size=8,color =dic_colors[n_cluster])))
    
    # agregar coordenada central
    fig.add_trace(go.Scattermapbox(
            name = f'Planta ATE',
            lon = np.array(lon[0]),
            lat = np.array(lat[0]),
            mode="markers",
            marker =go.scattermapbox.Marker(size=8,color ='red')))
    
    # crear leyenda
    legend=dict(
            x=0,
            y=1,
            title_font_family="Tunga",
            font=dict(
                family="Tunga",
                size=15,
                color="black"
            ),
            bgcolor="white",
            bordercolor="Black",
            borderwidth=2)
    
    # hacer update de leyenda
    fig.update_layout(legend=legend,legend_title_text=f'Ruta para el cluster {n_cluster}',mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
            mapbox = {'center': {'lat': lat_center, 
                                'lon': lon_center
                                }, 
                    'zoom': zoom},
                    showlegend=True)
    # plotear
    fig.show()

def presentar_ruta(df_in,arcos):
    # quitar la planta ATE de los puntos (la cual está en los extremos) y restar el valor de 1
    # para que se acomode a los índices reales del dataframe
    list_puntos_venta=np.array(arcos[1:-1])-1
    
    # definir dataframe a devolver cuyas rutas están por orden acorde a los arcos
    df_sorted=pd.DataFrame()
    
    # llenar el dataframe acorde a list_puntos_venta los cuales están ordenados y los registros se obtienen
    # del .iloc del dataframe que ingresa
    for i in list_puntos_venta:
        df_sorted=df_sorted.append(df_in.iloc[i].to_dict(),ignore_index=True)
        
    # retornar dataframe ordenado por arcos a seguir según la ruta optimizada por cplex
    return df_sorted