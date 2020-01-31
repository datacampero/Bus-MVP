
from buslinesim import Bus, Simulation, Event, BusStop, PrettyFig, Stats
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
import pandas as pd
from scipy import stats
import subprocess
import heapq



def parametros(paradas, intervalo, dist_pasajeros, cant_autobuses, tiempo_screen=1, vel_autobus=0.83):
    """ paradas: (array np) donde cada posicion es la distancia en Km entre una parada y otra
        intervalo: (INT) es cada cuantos minutos un autobus sale min/autobus
        dist_pasajeros: (FLOAT) ""Tiempo entre dos llegadas sucesivas de pasajeros a una parada de autobús min/pasajero
        cant_autobuses: (INT) es la cantidad de autobuses que van a salir en la simulacion
        tiempo_screen: (INT)  "Tiempo en que la simulacion hace un screen para mostrar resultados (por default es cada minuto)
    """
    stop_pos = paradas
    nb_stops = len(stop_pos)
    mean_stops = nb_stops/2.0
    std_stops = nb_stops/4.0
    a, b = (1 - mean_stops)/std_stops, (nb_stops - mean_stops)/std_stops
    stops_to_dest = lambda: np.round(truncnorm.rvs(a, b, loc=mean_stops, scale=std_stops))
    sim = Simulation(bus_stop_positions=stop_pos,
                     time_between_buses=lambda: intervalo,
                     nb_stops_to_dest=stops_to_dest,
                     passenger_arrival_times=lambda : np.random.exponential(dist_pasajeros),
                     stats_time=1, nb_buses=cant_autobuses, bus_speed=lambda: truncnorm.rvs(-2, 2, loc=vel_autobus, scale=0.1))
    sim.run()
    avg_nb_passengers = [nb_passengers.mean() for nb_passengers in sim.stats.nb_passengers_in_active_buses]
    sim.stats.t = np.array(sim.stats.t)
    tiempos = sim.stats.t.tolist()
    horas= sim.stats.t/60
    horas = horas.tolist()

    horas = [ '%.2f' % elem for elem in horas ]
    dict = {'tiempo en minutos': tiempos, 'tiempo en horas': horas, 'Nro de pasajeros en Buses Activos': avg_nb_passengers}  
    dfnropasajbuses = pd.DataFrame(dict) 

    diccionario = {'Promedio de satisfaccion de pasajeros':np.mean(sim.stats.satisfaction), 
        'Cantidad de pasajeros que llegaron a su destino':len(sim.stats.travel_times), 
        'Promedio de tiempo de viaje total':np.mean(sim.stats.travel_times),
        'Cant de pasajeros que esperaron': len(sim.stats.waited_times),
        'Promedio de tiempo de de espera en cola':np.mean(sim.stats.waited_times),
        'Media del numero de paradas que recorre cada pasajero':np.mean(sim.stats.nb_stops_traveled),
        'Valor mas frecuente del numero de paradas que recorre cada pasajero':int(stats.mode(sim.stats.nb_stops_traveled)[0]),
        'Numero de intervalos de los histogramas':int(sim.stats._nb_bins(len(sim.stats.travel_times))),
        'Promedio del numero de pasajeros que llevo un autobus':np.mean(sim.stats.total_passengers[-1])
       }  
    return dfnropasajbuses



if __name__ == '__main__':
    parametros([ 0,  4,  15,  18,  30, 35, 42, 50], 5,15, 15)

