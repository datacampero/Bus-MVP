from flask import *
import pandas as pd
import datetime
import numpy as np
app = Flask(__name__)

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
    time_table
    time_table, time, final = next_trip(time_table, time= datetime.datetime(2019, 7, 12, 6, 0, 0), stop=a, routes=routes)
    time_table =  assign_full_trips(time_table, headways, a, routes)
    time_table = asssign_full_blocks(time_table, routes)
    return render_template('view.html',tables=[time_table.to_html(classes='female'), time_table.to_html(classes='male')],
    titles = ['na', 'Planificado', 'Simulado'])

@app.route("/")
def menu_page():
    return render_template("index.html")




if __name__ == "__main__":
    app.run(debug=True)