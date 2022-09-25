import plotly.graph_objects as go

def entrenar_cluster(df_done,df_cleaned,tipo_cluster,n_components):
    # definir dataframe para clustering
    df_cluster=df_done[['Latitud','Longitud']].copy()

    # entrenar modelo de clustering
    cluster=tipo_cluster(n_components).fit(df_cluster)

    # obtener labels
    labels=cluster.predict(df_cluster)

    # devovler dataframe con labels
    df_export=df_cleaned.copy()
    df_export.loc[:,'Cluster']=labels
    return df_export.sort_values(by='Cluster')

def plot_clusters(df_export):
    # crear diccionario de colores
    colors=['#8B8378','#00FFFF','#76EEC6','#838B8B','#E3CF57','#0000FF','#00008B','#8A2BE2','#9C661F','#FF4040',
    '#98F5FF','#FF6103','#7FFF00','#DC143C','#68228B','#C1FFC1','#00BFFF','#FF1493','#ADFF2F','#191970',
    '#FF8247','#800000','#FFE4E1']
    n_cluster=range(0,23)
    dic_colors=dict(zip(n_cluster,colors))

    # establecer centros para iniciar el mapa
    lat_center = df_export.Latitud.mean()
    lon_center = df_export.Longitud.mean()

    # inicializar la figura
    fig=go.Figure()

    # iterar por cada cluster
    for i in df_export.Cluster.unique():
        flag=df_export.loc[df_export.Cluster==i]
        fig.add_trace(go.Scattermapbox(
            name = f'Cluster {i}',
            lon = flag.Longitud,
            lat = flag.Latitud,
            mode="markers",
            marker =go.scattermapbox.Marker(size=8,color =dic_colors[i])))

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
            borderwidth=2
        )
    # hacer update de leyenda
    fig.update_layout(legend=legend,legend_title_text=f"""Clusters {df_export['Día'][0].upper()}""",
                        mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox = {'center': {'lat': lat_center, 'lon': lon_center}, 
                                'zoom': 10},
                        showlegend=True)
    # plotear
    fig.show()