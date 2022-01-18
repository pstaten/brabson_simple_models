import ipywidgets as widgets
from matplotlib import pyplot as plt
import numpy as np

slider_min = 0.1 # earth-distances
slider_max = 50 # earth-distances
slider_step = 0.1
slider_default = 1
earth_dist = 1.496e11 # average meters to the earth from the sun
T_sun = 5772. # effective temperature of the sun in Kelvins
r_sun = 6.96e8 # average radius of the sun, about 696,000,000 kilometers

def calc_temp_from_sun(distance):
    t_bb = T_sun * (r_sun**2./(distance)**2./4.)**0.25
    return(t_bb)

# set up plot
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_ylim(30, 900)
ax.set_xlim(0.1, 50)
ax.set_xlabel('Distance from the sun in Astronomical Units (AU)')
ax.set_ylabel('Temperature in Kelvins (K)')
ax.set_title('Simplest Model output with planets (and Pluto)')
ax.set_yscale('log')
ax.set_yticks((30, 60, 90, 300, 600, 900), labels=('30', '60', '90', '300', '600', '900'))

@widgets.interact(AU=(slider_min, slider_max, slider_step))
def update(AU=slider_default):
    """Remove old lines from plot and plot new one"""
    [l.remove() for l in ax.lines]
    ax.plot(0.4, 398.15, '.', color='gray') #Mercury
    #ax.text(0.4, 398.15, '.M', color='gray') #Mercury
    ax.plot(0.72, 744.15, '.', color='gold') #Venus
    #ax.text(0.72, 744.15, '.V', color='gold') #Venus
    ax.plot(1, 289.15, '.', color='blue') #Earth
    #ax.text(1, 289.15, '.E', color='blue') #Earth
    ax.plot(1.52, 245.15, '.', color='red') #Mars
    #ax.text(1.52, 245.15, '.M', color='red') #Mars
    ax.plot(5.2, 165.15, '.', color='orange') #Jupiter
    #ax.text(5.2, 165.15, '.J', color='orange') #Jupiter
    ax.plot(9.5, 135.15, '.', color='maroon') #Saturn
    #ax.text(9.5, 135.15, '.S', color='maroon') #Saturn
    ax.plot(19.8, 78.15, '.', color='teal') #Uranus
    #ax.text(19.8, 78.15, '.U', color='teal') #Uranus
    ax.plot(30, 72.15, '.', color='blue') #Neptune
    #ax.text(30, 72.15, '.N', color='blue') #Neptune
    ax.plot(49, 40, '.', color='steelblue') #Pluto
    #ax.text(49, 40, '.P', color='steelblue') #Pluto
    planet_temp = calc_temp_from_sun(earth_dist*AU)
    ax.plot(AU, planet_temp, 'ok', fillstyle='none')
    print('Modeled temperature: {:.0f} K'.format(planet_temp))
