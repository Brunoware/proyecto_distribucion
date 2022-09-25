import numpy as np
import plotly.graph_objects as go

def escoger_variables(df,columns):
    # limpiar columnas
    df.columns=[i.strip() for i in df.columns]
    return df[columns].copy()

def isfloat(num):
    try:
        float(num)
        return True
        
    except ValueError:
        return False

def limpiar_dataframe(df):
    # definir tipos de variable
    tipo_variable={'Fecha':np.datetime64,'Ce.':str,'Día':str,'Interlocut':str,'Ruta real':str,'Distrito':str,
                   'Cliente':str,'D.Solic/Ct':str,'Dirección':str,'Latitud':float,'Longitud':float,'Pedido':float,
                   'Real':float,'T.Ruta':str}
    
    # Asignar la menor clase
    df.loc[df['T.Ruta'].isnull(),'T.Ruta']='R.secundario'
    
    # Eliminar valores nulos
    df.dropna(subset=['Latitud','Longitud'],inplace=True,axis=0)
    
    # Eliminar registros indefinidos
    index_indefinidos=df.loc[(df['Latitud'].apply(lambda x:isfloat(x))==False)|(df['Longitud'].apply(lambda x:isfloat(x))==False)].index.tolist()
    df=df.drop(index=index_indefinidos).reset_index(drop=True)
    
    # cambiar tipo de variable 
    for i in df.columns:
        df[i]=df[i].astype(tipo_variable[i])
        
    # retornar dataframe limpio
    return df

def plot_raw_map(df,dia):
    df_one=df.loc[df['Día']==dia].copy()
    # coordenadas del centro
    lat_center = df_one.Latitud.mean()
    lon_center = df_one.Longitud.mean()

    # inicializar la figura
    fig=go.Figure()
    # diccionario de colores
    dia_color={'lunes':'lightcoral','martes':'gold','miércoles':'lime','jueves':'hotpink','viernes':'dodgerblue','sábado':'peru'}
    # iterar por cada cluster
    fig.add_trace(go.Scattermapbox(
        name = f'Puntos de venta del día {dia}',
        lon = df_one.Longitud,
        lat = df_one.Latitud,
        mode="markers",
        marker =go.scattermapbox.Marker(size=8,color =dia_color[dia])))

    # crear leyendad
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
            borderwidth=2
        )
    # hacer update de leyenda
    fig.update_layout(legend=legend,legend_title_text='Puntos de distribucion',mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
            mapbox = {'center': {'lat': lat_center, 
                                'lon': lon_center
                                }, 
                    'zoom': 10},
                    showlegend=True)
    # plotear
    fig.show()