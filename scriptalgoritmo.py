import psycopg2
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import math


#Locations Dataframe
def deflocations():
    indexlocations = [1,2,3,4,5,6,7,8,9,10]
    locations = ['Chacao','Chacaito','Sabana Grande','Plaza Venezuela','Altamira','CCCT','El Marques','Los Dos Caminos','Parque del Este','Los Ruices']
    dict = {'id ':indexlocations ,'location': locations  }  
    df = pd.DataFrame(dict) 
    return df

#distance Dataframe
def defdistance():
    idtable = [1,2,3,4,5,6,7,8,9]
    first = [1,2,3,4,5,6,7,8,9]
    Next =[2,3,4,5,6,7,8,9,10]
    distance = [0.9,0.8,0.9,0.9,1.0,0.9, 1.2,0.9,0.8]
    dict2 = {'id ':idtable ,'first stop': first, 'next stop': Next, 'distance (Km)': distance  }  
    df_distances = pd.DataFrame(dict2) 
    return df_distances

#arrivals Dataframe
def defarrivals():
    ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
    busstop_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    passengers = [13.0, 14.0, 12.5, 14.5, 12.5, 12.0, 7.5, 2.0, 3.5, 0.0, 6.0, 5.0, 6.0, 5.0, 6.0, 3.5, 4.0, 3.0, 1.0, 0.0, 15.0, 10.5, 14.5, 10.5, 10.5, 9.5, 10.5, 10.5, 2.5, 0.0, 3.0, 3.0, 3.5, 3.0, 2.5, 2.5, 2.0, 2.0, 1.0, 0.0, 4.5, 5.5, 5.0, 3.5, 4.5, 3.5, 2.0, 2.0, 1.5, 0.0, 15.0, 13.5, 16.0, 14.5, 10.0, 10.5, 10.0, 7.5, 2.5, 0.0]
    schedule = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
    starthour=['08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', '08:00:00', 
                '10:00:00', '10:00:00', '10:00:00', '10:00:00', '10:00:00', '10:00:00','10:00:00' ,'10:00:00' , '10:00:00', '10:00:00',
                '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00',
                '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00',
                '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00',
                '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00']

    finishhour=['10:00:00', '10:00:00', '10:00:00', '10:00:00', '10:00:00', '10:00:00', '10:00:00' ,'10:00:00' ,'10:00:00', '10:00:00',
                '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00', '12:00:00',
                '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00', '14:00:00',
                '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00', '16:00:00',
                '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00', '18:00:00',
                '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00', '20:00:00']

    dict3 = {'id ':ids ,'busstop id': busstop_id, 'passengers':passengers,'schedule': schedule, 'start hour': starthour, 'finish hour': finishhour }  
    df_arrivals = pd.DataFrame(dict3) 
    return df_arrivals

def timetravel(vel, cap, df_distances):
    distance_total = df_distances['distance (Km)'].sum()
    distance_total = int(distance_total)
    duration_travel = distance_total/vel
    return duration_travel

def calculationheadway(cost1,cost2, df_arrivals, duration_travel):
    dfpassengers = df_arrivals[['schedule', 'passengers']].groupby(['schedule']).sum()
    passengers_list = dfpassengers['passengers'].tolist()
    count = 0
    dicc = {'id_schedule':[], 'bus_headway':[]}
    dicc2 = {'id_schedule':[], 'bus_headway':[]}
    dicc3 = {'id_schedule':[], 'bus_headway':[]}
    for sqll in passengers_list:
        count +=1
        def objective(x):
            x1 = x[0] #headway in minutes
            return ((cost1/2)*sqll*x1**2)+(cost2*duration_travel/x1)

        def constraint1(x):
            return x[0]-0
        con1 = {'type': 'ineq', 'fun': constraint1}
        x0=[1]
        sol = minimize (objective,x0,method='SLSQP', constraints = [con1])

        dicc['id_schedule'].append(count) 
        dicc['bus_headway'].append(sol.x[0])
        dicc2['id_schedule'].append(count) 
        dicc2['bus_headway'].append(round(sol.x[0]))
        dicc3['id_schedule'].append(count) 
        dicc3['bus_headway'].append(math.trunc(sol.x[0]))
        
    headway = pd.DataFrame(dicc)
    headway2 = pd.DataFrame(dicc2)
    headway3 = pd.DataFrame(dicc3)
    return headway, headway2, headway3




