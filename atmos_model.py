import ipywidgets as widgets
from matplotlib import pyplot as plt
import numpy as np

def run_atmos_model(albedo=0.3, solar_constant = 1.36e3/4., emiss_atm = 0.2, n_layers = 10):
    # define a bunch of constants we'll use later
    sb_const = 5.670367e-8 #W⋅m -2
    sp_heat_capacity_water = 4.2e3 # J/kg/Kelvin
    density_water = 1000 # kg/m^3
    sp_heat_capacity_air = 1005 # J/kg/Kelvin
    gravity = 9.81 # ms^-2

    n_seconds = 60.*60.*24. # one-day timestep

    t_surf = 273.15 # Kelvins; initial temperature only

    # initialize arrays to hold data later
    emissivity = np.zeros(n_layers) + emiss_atm
    heat_upward = np.zeros(n_layers+1)
    heat_dnward = np.zeros(n_layers+1)
    t_atm = np.zeros(n_layers) + 273.15

    # ground heat capacity; assume 1-meter mixed layer depth
    heat_capacity_ground = sp_heat_capacity_water * density_water

    # atmosphere heat capacity; divide the 1000 hPa of atmosphere evenly into n_layers chunks
    if n_layers >= 1:
        heat_capacity_atm = 100000./n_layers*gravity*sp_heat_capacity_air

    #heat from the sun
    sun_reflected = solar_constant*albedo
    heat_from_the_sun = solar_constant - sun_reflected
    
    for jj in range(40000):
        heat_upward[0] = sb_const * t_surf**4.
        heat_dnward[-1] = 0 # ignore downward infrared
        if n_layers >= 1:
            for ii in range(n_layers):
                # remove heat absorbed from below from the amount emitted above
                emit_ii = sb_const*emissivity[ii]*t_atm[ii]**4.
                absorb_from_below_ii = emissivity[ii]*heat_upward[ii]
                heat_upward[ii+1] = heat_upward[ii]-absorb_from_below_ii+emit_ii
            for ii in range(n_layers-1,-1,-1):
                emit_ii = sb_const*emissivity[ii]*t_atm[ii]**4.
                absorb_from_above_ii = emissivity[ii]*heat_dnward[ii+1]
                heat_dnward[ii] = heat_dnward[ii+1]-absorb_from_above_ii+emit_ii
                #print(ii, heat_dnward[ii+1],absorb_from_above_ii,emit_ii, heat_dnward[ii])

        # calculate changes in temperature based on heating
        t_surf += (heat_from_the_sun + heat_dnward[0] - heat_upward[0]) / heat_capacity_ground * n_seconds
        if n_layers >= 1:
            for ii in range(n_layers):
                t_atm[ii] += (heat_upward[ii]-heat_upward[ii+1]+heat_dnward[ii+1]-heat_dnward[ii]) / heat_capacity_atm * n_seconds

    if n_layers >= 1:        
        levdiff = 1000./n_layers
        plevels = np.insert(np.array([1010, 0, -200]), 1, 1000.-levdiff*np.arange(n_layers))

        t_all = np.insert(np.array([t_surf, t_atm[-1], t_atm[-1]]), 1, t_atm)
        ax.pcolormesh([200, 1000], plevels, np.transpose(np.tile(t_all, (2,1))), cmap='bone')
        [l.remove() for l in ax.lines]
        ax.plot(t_all[:-2], plevels[:-2], color='deepskyblue')
    else:
        levdiff = 100
        plevels = np.array([1010, 0, -200])
        ax.pcolormesh([200, 1000], plevels, np.zeros((3, 2)))

    max_heat = np.max(np.array([np.max(heat_upward), heat_from_the_sun, sun_reflected]))
    max_w = 40
    up_w = max_w * heat_upward / max_heat
    dn_w = max_w * heat_dnward / max_heat
    sun_dn_w =  max_w * solar_constant / max_heat
    sun_up_w = max_w * sun_reflected / max_heat

    ax.arrow(850, 1010, 0, -levdiff*.5, width = up_w[0], head_width=up_w[0]*2., fc='red', ec='red')
    if n_layers >= 1:
        for ii in range(2, n_layers+1):
            plt.arrow(950, plevels[ii], 0, levdiff*.5, width=dn_w[ii], head_width=dn_w[ii]*2., fc='red', ec='red')
            plt.arrow(850, plevels[ii], 0, -levdiff*.5, width=up_w[ii], head_width=up_w[ii]*2., fc='red', ec='red')
    ax.arrow(600, 0, 0, 950, width = sun_dn_w, head_width= sun_dn_w*4., fc='yellow', ec='gold')
    ax.arrow(700, 1000, 0, -1000, width = sun_up_w, head_width= sun_up_w*4., fc='yellow', ec='gold')

    
    [t.remove() for t in ax.texts]
    ax.text(t_surf, 1000, '{:.0f} K'.format(t_surf), color='deepskyblue')
    ax.text(600, -180, '{:.0f}'.format(solar_constant) + r' Wm$^{-2}$', color='yellow', ha='center', va='top', bbox=dict(facecolor='black', alpha=0.5))
    ax.text(700, -120, '{:.0f}'.format(sun_reflected) + r' Wm$^{-2}$', color='yellow', ha='center', va='top', bbox=dict(facecolor='black', alpha=0.5))
    ax.text(850, -120, '{:.0f}'.format(heat_upward[-1]) + r' Wm$^{-2}$', color='red', ha='center', va='top', bbox=dict(facecolor='black', alpha=0.5))
    ax.set_xticks([200, 300, 400, 500, 600, 700, 850, 950], labels=['200', '300', '400', '500', 'solar\ndown', 'solar\nup', 'thermal\nup', 'thermal\ndown'])
    ax.set_yticks([1000, 0], labels=('surface', 'space'))
    ax.axvline(500, color='black', linewidth=0.75)
    ax.text(350, 0, 'temperature', color='deepskyblue', ha='center')
    ax.set_title('Multi-layer greenhouse atmosphere model')
    ax.set_ylim(1010, -200)
    ax.set_xlim(200, 1000)

# create the user interface
b_update = widgets.Button(description='update')
b_reset = widgets.Button(description='reset sliders')
sl_albedo = widgets.IntSlider(description='albedo %', min=0, max=90, step=10, value=30, continuous_update=False)
sl_solar = widgets.IntSlider(description='solar constant %', min=80, max=200, step=10, value=100, continuous_update=False)
sl_emiss = widgets.IntSlider(description='greenhouse %', min=10, max=100, step=10, value=20, continuous_update=False)
sl_layers = widgets.IntSlider(description='# layers', min=0, max=25, value=10, continuous_update=False)

output = widgets.Output()
with output:
    fig, ax = plt.subplots()
    
def update_plot(b):
    with output:
        ax.cla()
        run_atmos_model(albedo=sl_albedo.value/100., 
                        solar_constant=1.36e3/4. * sl_solar.value/100.,
                        emiss_atm=sl_emiss.value/100.,
                        n_layers=sl_layers.value)

def reset_values(b):
    sl_albedo.value = 30
    sl_solar.value = 100
    sl_emiss.value = 20
    sl_layers.value = 10
    #update_plot(None)

update_plot(None)

b_update.on_click(update_plot)
b_reset.on_click(reset_values)

sliders = widgets.VBox([sl_albedo, sl_solar, sl_emiss, sl_layers])
controls = widgets.HBox([sliders, b_update, b_reset])
#widgets.VBox([output, controls]) # for some reason it works better if this last line is in the notebook itself

'''# diagnostic printing I did during debugging
fig, ax = plt.subplots(1, 3)
ax[0].set_xlim(0,4)
ax[0].set_ylim(0, n_layers+1)
ax[0].text(0, 0, t_surf)
ax[0].text(1, 0.5, heat_upward[0], color='teal')
ax[0].text(2, 0.4, heat_dnward[0], color='red')
ax[0].text(3, 2.7, heat_from_the_sun, color='gold')
for ii in range(n_layers):
    ax[0].text(0, ii+1, t_atm[ii])
    ax[0].text(1, ii+1.5, heat_upward[ii+1], color='teal')
    ax[0].text(2, ii+1.4, heat_dnward[ii+1], color='red')
'''
