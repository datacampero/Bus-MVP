from flask import *
from flask import Flask, request, render_template, sessions #backend
import pandas as pd
import datetime
import numpy as np
app = Flask(__name__)
from scriptalgoritmo import (
    deflocations, defdistance, defarrivals, timetravel, calculationheadway
)

from functions import (
    parametros, df_passengers_activebus, df_number_activebus, df_queues_at_stops, _nb_bins, time_system, time_waiting, number_stops_traveled, satisfaction, numberpassengers
)

class stop:
    def __init__(self, name, terminal, layover, next_stop, time_next_stop):
        self.terminal = terminal
        self.name = name
        self.layover = layover
        self.next_stop = next_stop
        self.time_next_stop = time_next_stop
    def set_next(self,stop, time, med, desv):
        self.next_stop = stop
        self.time_next_stop = time
        self.med= med
        self.desv = desv

def next_trip(time_table, time, stop, routes):
    #Si existe un viaje a la misma hora, regresa la misma tabla
    if(len(time_table[time_table[str(routes.index(stop))] == time])>0):
        return time_table, time, time
    row={}
    first_stop = stop
    next_stop = stop.next_stop
    running = 0
    init_time = time
    while True:
        #Indice de la columna en la parada actual
        index = routes.index(stop)
        #Tiempo de la anterior + el Running
        time = time + datetime.timedelta(minutes =running)
        row[str(index)] = time 
        #Si es terminal, agregar el layover
        if(stop.terminal == True and stop!=first_stop):
            time = time + datetime.timedelta(minutes =stop.layover)
            row[str(index+1)] = time 
        #Ir a la siguiente parada
        running = stop.time_next_stop
        stop = next_stop
        next_stop = stop.next_stop
        #Si la actual es igual a la primera, actualizar la ultima columna y salir
        if(stop == first_stop):   
            ftime = time + datetime.timedelta(minutes =running)
            row[str(index+1)] = time + datetime.timedelta(minutes =running)
            break       
        
    time_table = time_table.append(row, ignore_index=True)
    return time_table, init_time, ftime

def assign_next_trip(time_table, routes, min_layover=10, time= None ):
    final_stop_column = 1 + len(routes)
    first_stop_column = 2
    nt_column = 2+len(routes)
    block = time_table['Block#'].max()
    if(block is pd.NaT):
        block = 1 
    elif(time == None):
        block +=1
    if(time==None):
        row = time_table[time_table.NextTrip.isnull()].head(1)
        index = time_table[time_table.NextTrip.isnull()].head(1).index[0]
        time_table.iloc[index, 0] = block
        termina = row.iloc[:,final_stop_column].dt.to_pydatetime()[0] + datetime.timedelta(minutes = min_layover)
    else:
        row = time_table[time_table.iloc[:,first_stop_column] == time]
        assert len(row) == 1
        index = time_table[time_table.iloc[:,first_stop_column] == time].index[0]
        time_table.iloc[index, 0] = block
        termina = row.iloc[:,final_stop_column].dt.to_pydatetime()[0]

    prox_comienzo = time_table[time_table.iloc[:,first_stop_column] >= termina]
    prox_comienzo = prox_comienzo[prox_comienzo['Block#'].isnull()]
    if(len(prox_comienzo) > 0 ):
        prox_comienzo = prox_comienzo[prox_comienzo['Block#'].isnull()]
        prox_comienzo = prox_comienzo.iloc[:,first_stop_column].dt.to_pydatetime().min()    
        time_table.iloc[index, nt_column] = prox_comienzo
        return time_table, prox_comienzo, block
    else:        
        time_table.iloc[index, nt_column] = 0
        return time_table, -1, -1
#assign_next_trip(time_table, min_layover=10, time= None)

def assign_full_trips(time_table, headways, a, routes):
    #Llenar tiempos
    for headway, spam_service in headways:
        time_table, time, ftime = next_trip(time_table, time= spam_service[0], stop=a, routes=routes)
        #print('For: ', time)
        while time < spam_service[1]:
            n_time = time + datetime.timedelta(minutes = headway)
            time_table, time, ftime =  next_trip(time_table, time= n_time, stop=a, routes=routes)
    return time_table

def asssign_full_blocks(time_table, routes):
    prox_comienzo = None
    block = 1
    while block != 0:
        while prox_comienzo != -1:
            time_table, prox_comienzo, block = assign_next_trip(time_table, routes, min_layover=10, time=prox_comienzo)            
            #print(prox_comienzo, block)
        prox_comienzo = None
        block = len(time_table[time_table['Block#'].isnull()])
    return time_table


def next_trip2(time_table, time, route):
    row=time_table
    stop = route[0]
    first_stop = route[0]
    next_stop = stop.next_stop
    running = 0
    init_time = time
    while True:
        #Indice de la columna en la parada actual
        index = route.index(stop)
        #Tiempo de la anterior + el Running
        time = time + datetime.timedelta(minutes =running)
        plan_time =  time_table[str(index)] 
        row[str(index)] = time 
        #print(time -plan_time)
        #Si es terminal, agregar el layover
        if(stop.terminal == True and stop!=first_stop):
            time = time + datetime.timedelta(minutes =stop.layover)
            row[str(index+1)] = time 
        #Ir a la siguiente parada
        running = stop.time_next_stop
        running = running + np.random.normal(stop.med, stop.desv, 1)[0]
        stop = next_stop
        next_stop = stop.next_stop
        #Si la actual es igual a la primera, actualizar la ultima columna y salir
        if(stop == first_stop):   
            ftime = time + datetime.timedelta(minutes =running)
            row[str(index+1)] = time + datetime.timedelta(minutes =running)
            break       
    return row, ftime, time_table['NextTrip']


@app.route("/tables")
def show_tables():
    #AM
    spam_service1 = [datetime.datetime(2019, 7, 12, 6, 0, 0), datetime.datetime(2019, 7, 12, 10, 0, 0)]
    spam_service2 = [datetime.datetime(2019, 7, 12, 8, 0, 0), datetime.datetime(2019, 7, 12, 10, 0, 0)]
    spam_service3 = [datetime.datetime(2019, 7, 12, 10, 0, 0), datetime.datetime(2019, 7, 12, 12, 0, 0)]
    #PM
    spam_service4 = [datetime.datetime(2019, 7, 12, 12, 0, 0), datetime.datetime(2019, 7, 12, 14, 0, 0)]
    spam_service5 = [datetime.datetime(2019, 7, 12, 14, 0, 0), datetime.datetime(2019, 7, 12, 16, 0, 0)]
    spam_service6 = [datetime.datetime(2019, 7, 12, 16, 0, 0), datetime.datetime(2019, 7, 12, 18, 0, 0)]
    headways = [(30, spam_service1), (15, spam_service2), (30, spam_service3), (30, spam_service4), (15, spam_service5), (30, spam_service6)]
    routes=[]
    a = stop('A', True, 12, None,None)
    routes.append(a)
    b = stop('B', False, 0, None,None)
    routes.append(b)
    c = stop('C', False, 0, None,None)
    routes.append(c)
    d = stop('D', True, 12, None,None)
    routes.append(d)
    routes.append(d)
    e = stop('E', False, 0, None,None)
    routes.append(e)
    f = stop('F', False, 0, None,None)
    routes.append(f)

    routes.append(a)
    a.set_next(b, 8, 2, 1)
    b.set_next(c, 14, 3, 2)
    c.set_next(d, 11, 2, 1)
    d.set_next(e, 11, 4, 2)
    e.set_next(f, 14, 3, 1)
    f.set_next(a, 8, 3, 2)

    cols = list(range(len(routes)))
    cols = [str(x) for x in cols]
    columns = ['Block#', 'PullOut']
    columns.extend(cols)
    columns.extend(['NextTrip','PullIn'])
    time_table = pd.DataFrame(columns=columns)
    time_table, time, final = next_trip(time_table, time= datetime.datetime(2019, 7, 12, 6, 0, 0), stop=a, routes=routes)
    time_table =  assign_full_trips(time_table, headways, a, routes)
    time_table = asssign_full_blocks(time_table, routes)
    time_table.sort_values('0', inplace=True)


    sim_tt = pd.DataFrame()
    for b in time_table['Block#'].unique():
        ftime = None
        for row in time_table[time_table['Block#']==b].iterrows():
            if(ftime == None):
                ftime = rowftime = row[1]['0']
            r, ftime, ntrip = next_trip2(row[1], ftime, routes)
            if(row[1]['NextTrip']!= 0):
                if(ftime>row[1]['NextTrip']):
                    r['RealNextTrip'] = pd.Timestamp(ftime)
                else:
                    r['RealNextTrip'] = row[1]['NextTrip']
            sim_tt = sim_tt.append(r, ignore_index=True)

    sim_tt['RealNextTrip'] = pd.to_datetime(sim_tt['RealNextTrip'])
    sim_tt.sort_values('0')
    ordenado = sim_tt[['Block#','PullOut','0', '1', '2', '3', '4', '5', '6', '7', 'PullIn', 'NextTrip', 'RealNextTrip']]
    ordenado['RealNextTrip']=ordenado['RealNextTrip'].astype('datetime64[ns]')
    ordenado['NextTrip'] = ordenado['RealNextTrip']
    ordenado = ordenado.drop('RealNextTrip', 1)
    ordenado = ordenado.sort_values('0')
    ordenado.reset_index()

    return render_template('view.html',tables=[time_table.to_html(classes='female'), ordenado.to_html(classes='male')],
    titles = ['na', 'Planificado', 'Simulado'])



@app.route("/frecuencia", methods=['GET','POST'])
def calculate_headway():
    
    dist = defdistance()
    arrival = defarrivals()
    duration = timetravel(5,300,dist)
    head, head2, head3 = calculationheadway(0.24565,500, arrival, duration)
    return render_template('headway.html',tables=[head.to_html(classes='female'), head2.to_html(classes='male'),  head3.to_html(classes='sal') ],
    titles = ['na', 'Frecuencias para cada parada', 'Si aumentas los tiempos de espera, pero reduces el costo de servicio',  'Si disminuyes los tiempos de espera, pero aumentas el costo de servicio' ])


@app.route("/")
def menu_page():
    return render_template("index.html")



@app.route("/rar")
def steps():
    return render_template("steps.html")




@app.route("/simulacion", methods=['GET','POST'])
def simulacion():
    if request.method == 'POST':
        interv = request.form.get("inter", False)
        dicc, sim = parametros([ 0,  4,  15,  18,  30, 35, 42, 50], interv,15, 15)
        simu = pd.DataFrame(dicc, index=[0]) 
        df1 = df_passengers_activebus(sim)
        df2 = df_number_activebus(sim)
        df3 = df_queues_at_stops(sim)
        df4 = time_system(sim)
        df5 = time_waiting(sim)
        df6 = number_stops_traveled(sim)
        df7 = satisfaction(sim)
        df8 = numberpassengers(sim)
        return render_template('simulacion.html',tables=[
        simu.to_html(classes='female'), 
        df1.to_html(classes='female'),
        df2.to_html(classes='female'), 
        df3.to_html(classes='female'), 
        df4.to_html(classes='female'), 
        df5.to_html(classes='female'),
        df6.to_html(classes='female'), 
        df7.to_html(classes='female'), 
        df8.to_html(classes='female')
        ],
        titles = ['na', 'Datos de la Simulacion', 'Pasajeros en Buses Activos', 'Numero de buses Activos', 'Cola por parada', 'Tiempo en el sistema', 'Tiempo de espera', 'Numero de parada recorridas', 'Satisfaccion de tiempo de espera', 'Numero de pasajeros' ])


@app.route("/graf")
def graf_page():
    return render_template("graficos.html")

@app.route("/video")
def video_page():
    return render_template("video.html")

if __name__ == "__main__":
    app.run(debug=True)