import ipywidgets as widgets
import numpy as np
from matplotlib import gridspec
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from math import isclose

def proport(pi_amount, pi_flux, current_amount, verbose=False):
    k_constant = pi_flux/pi_amount
    current_flux = k_constant * current_amount
    if verbose:
        print(pi_amount, pi_flux, current_amount, current_flux)
    return current_flux

def linear_extrap(pi_amount, y2k_amount, current_amount, pi_flux, y2k_flux, verbose=False):
    rise_over_run = (y2k_flux - pi_flux) / (y2k_amount - pi_amount)
    dx = current_amount - pi_amount
    current_flux = pi_flux + dx*rise_over_run
    if verbose:
        print(pi_amount, y2k_amount, current_amount, pi_flux, y2k_flux, current_flux)
    return current_flux

def flux_arrow(ax, x0, y0, dx, dy, flux, piflux):
    base_width=5
    arrow_width = base_width*flux/piflux
    #print(arrow_width)
    if isclose(flux, piflux, rel_tol=1e-3, abs_tol=1e-3):
        color='black'  
    elif flux>piflux:
        color='red'
    else:
        color='gray'
    ax.arrow(x0, y0, dx, dy, width=arrow_width, head_width=15, ec=color, fc=color)

def net_up_arrow(ax, x0, y0, dy, flux, piflux):
    base_width=5
    arrow_width = base_width*flux/piflux
    if flux < 0:
        y0 += dy - 25
        dy *= -1
    abs_flux = abs(flux)
    abs_piflux = abs(piflux)
    if isclose(abs_flux, abs_piflux, rel_tol=1e-3, abs_tol=1e-3):
        color='black'  
    elif abs_flux>abs_piflux:
        color='red'
    else:
        color='gray'
    ax.arrow(x0, y0, 0, dy, width=arrow_width, head_width=15, ec=color, fc=color)

def run_model(ax0, ax1, humans=True, n_iterations = 1000, buffered_up_ocn=False, buffered_down_ocn=False, buffered_up_veg=False, buffered_down_veg=False, proportionate=False):
    atmosphere_n_0 = 589
    atmosphere_a_0 = 589 + 240
    fuel_reserves_n_0 = 1500
    fuel_reserves_a_0 = 1500 + 375
    vegetation_n_0 = 455
    vegetation_a_0 = 455 + 20
    soil_0 = 1900
    permafrost_0 = 1700
    surface_ocean_n_0 = 900
    deep_ocean_0 = 37100
    extra_in_ocean = 155
    surface_ocean_a_0 = 900 + 155
    marine_biota_0 = 3
    dissolved_organic_0 = 700
    rvr2sea_n = 0.9

    # natural fluxes
    rock2rivr_n = 0.1    # from rock
    burial_n = 0.2    # burial from rivers
    atm2rivr_n = 0.3        # rock weathering by rivers
    soil2rivr_n = 1.7        # exports from soil to rivers
    veg2soil_n = 1.7        # a missing number from the figure
    sfc2bio_n = 50        # surface-biota exchange
    bio2sfc_n = 37        # surface-biota exchange
    bio2doc_n = 2        # biota-DOC exchanges
    doc2deep_n = 2        # DOC-deep ocean exchange
    bio2deep_n = 11        # biota-deep exchange
    rivr2atm_n = 1.        # freshwater outgassing
    # surface ocean & deep ocean exchanges
    # the balance from the book has a bit extra going to the deep sea
    sfc2deep_n = 88.2 # 90 is what's in the figure; I tweaked it for balance
    deep2sfc_n = 101
    sfc2atm_n = 60.7
    atm2sfc_n = 60
    sfc2atm_a = 60.7 + 17.7
    atm2sfc_a = 60 + 20
    veg2atm_n = 107.2
    atm2veg_n = 108.9
    veg2atm_a = 107.2 + 11.6
    atm2veg_a = 108.9 + 14.1
    deep2rock_n = 0.2
    rivers_n = rock2rivr_n+atm2rivr_n+soil2rivr_n

    atmosphere = np.zeros(n_iterations)
    fuel_reserves = np.zeros(n_iterations)
    vegetation = np.zeros(n_iterations)
    deep_ocean = np.zeros(n_iterations)
    soil = np.zeros(n_iterations)
    permafrost = np.zeros(n_iterations)
    surface_ocean = np.zeros(n_iterations)
    marine_biota = np.zeros(n_iterations)
    dissolved_organic = np.zeros(n_iterations)

    # initialize the reservoirs
    
    atmosphere[0] = atmosphere_n_0
    fuel_reserves[0] = fuel_reserves_n_0
    vegetation[0] = vegetation_n_0
    deep_ocean[0] = deep_ocean_0
    soil[0] = soil_0
    permafrost[0] = permafrost_0
    marine_biota[0] = marine_biota_0
    dissolved_organic[0] = dissolved_organic_0
    
    if humans:
        atmosphere[0] = atmosphere_a_0
        fuel_reserves[0] = fuel_reserves_a_0
        vegetation[0] = vegetation_a_0
        surface_ocean[0] = surface_ocean_a_0
    else:
        atmosphere[0] = atmosphere_n_0
        fuel_reserves[0] = fuel_reserves_n_0
        vegetation[0] = vegetation_n_0
        surface_ocean[0] = surface_ocean_n_0
    
    for ii in range(1, n_iterations):
        atmosphere_change = 0
        fuel_reserves_change = 0
        vegetation_change = 0
        deep_ocean_change = 0
        soil_change = 0
        permafrost_change = 0
        surface_ocean_change = 0
        marine_biota_change = 0
        dissolved_organic_change = 0
        rivers = 0
        
        # we're going to keep a constant weathering rate here to get the rivers started
        rock2rivr = rock2rivr_n    
        
        rivers += rock2rivr
        # how much the rivers get in them from the atmosphere and soil may depend on
        # how much carbon is in them
        if proportionate:
            atm2rivr = proport(atmosphere_n_0, atm2rivr_n, atmosphere[ii-1])
            soil2rivr = proport(soil_0, soil2rivr_n, soil[ii-1])
        else:
            atm2rivr = atm2rivr_n
            soil2rivr = soil2rivr_n  
        rivers += atm2rivr + soil2rivr
        
        if proportionate:
            #veg2soil = proport(vegetation_n_0, veg2soil_n, vegetation[ii-1])
            #sfc2bio = proport(surface_ocean_n_0, sfc2bio_n, surface_ocean[ii-1])
            sfc2bio = proport(surface_ocean[0], sfc2bio_n, surface_ocean[ii-1])
            bio2sfc = bio2sfc_n*sfc2bio/sfc2bio_n
            bio2doc = bio2doc_n*sfc2bio/sfc2bio_n
            bio2deep = bio2deep_n*sfc2bio/sfc2bio_n
            doc2deep = proport(dissolved_organic_0, doc2deep_n, dissolved_organic[ii-1])
            #sfc2deep = proport(surface_ocean_n_0, sfc2deep_n, surface_ocean[ii-1])
            sfc2deep = proport(surface_ocean[0], sfc2deep_n, surface_ocean[ii-1])
            deep2sfc = proport(deep_ocean_0, deep2sfc_n, deep_ocean[ii-1])
            burial = proport(rivers_n, burial_n, rivers)
            rivr2atm = proport(rivers_n, rivr2atm_n, rivers)
            deep2rock = proport(deep_ocean_0, deep2rock_n, deep_ocean[ii-1])
        else:
            sfc2bio = sfc2bio_n
            bio2sfc = bio2sfc_n
            bio2doc = bio2doc_n
            bio2deep = bio2deep_n
            doc2deep = doc2deep_n
            sfc2deep = sfc2deep_n
            deep2sfc = deep2sfc_n
            burial = burial_n
            rivr2atm = rivr2atm_n
            deep2rock = deep2rock_n

        # let's just assume we're done ruining all the plants
        veg2soil = vegetation[ii-1]-vegetation[0]

        # we waited to take these out till after other calculations
        atmosphere_change -= atm2rivr
        soil_change -= soil2rivr
        
        # now let's go ahead and remove stuff from the river
        rivers -= rivr2atm
        atmosphere_change += rivr2atm
        rivers -= burial
        
        vegetation_change -= veg2soil
        soil_change += veg2soil
        surface_ocean_change -= sfc2bio
        marine_biota_change += sfc2bio
        surface_ocean_change += bio2sfc
        marine_biota_change -= bio2sfc
        marine_biota_change -= bio2doc
        dissolved_organic_change += bio2doc
        dissolved_organic_change -= doc2deep
        deep_ocean_change += doc2deep
        marine_biota_change -= bio2deep
        deep_ocean_change += bio2deep
        surface_ocean_change -= sfc2deep
        deep_ocean_change += sfc2deep
        surface_ocean_change += deep2sfc
        deep_ocean_change -= deep2sfc
        deep_ocean_change -= deep2rock        # deep ocean to ocean floor

        # rivers empty into ocean
        rvr2sea = rivers
        surface_ocean_change += rvr2sea

        # volcanism
        # walters et al. has 0.1 but I'm using 0.3 to balance the natural model
        # walters et al. also has a nearly 2.0 imbalance between the surface and deep oceans
        # so another logical way to balance this would be to increase the net flux
        # to the ocean, but I didn't want to mess with that part of the carbon flux
        volc_n = 0.3
        atmosphere_change += volc_n

        if humans:

            # land use change
            vegetation_change -= 1.1
            atmosphere_change += 1.1

            # fossil fuels
            if fuel_reserves[ii-1] <= 0:
                to_burn = 0
            else:
                if fuel_reserves[ii-1] <= 4.8:
                    to_burn = fuel_reserves[ii-1]
                else: 
                    to_burn = 4.8 # 7.8 for fossil fuels + cement
            atmosphere_change += to_burn
            fuel_reserves_change -= to_burn

            # super rough guess at cement
            cement = 3
            atmosphere_change += cement
            
            # human-influenced ocean-to-atmosphere and atmosphere to ocean
            if buffered_up_ocn:
                sfc2atm = linear_extrap(surface_ocean_n_0, surface_ocean_a_0, surface_ocean[ii-1], sfc2atm_n, sfc2atm_a, verbose=False)
            else:
                                sfc2atm = sfc2atm_a
            if buffered_down_ocn:
                atm2sfc = linear_extrap(atmosphere_n_0, atmosphere_a_0, atmosphere[ii-1], atm2sfc_n, atm2sfc_a)
            else:
                atm2sfc = atm2sfc_a
                
            # human-influenced ocean-to-atmosphere and atmosphere to ocean
            if buffered_up_veg:
                veg2atm = linear_extrap(vegetation_n_0, vegetation_a_0, vegetation[ii-1], veg2atm_n, veg2atm_a, verbose=False)
            else:
                veg2atm = veg2atm_a
            if buffered_down_veg:
                atm2veg = linear_extrap(atmosphere_n_0, atmosphere_a_0, atmosphere[ii-1], atm2veg_n, atm2veg_a)
            else:
                atm2veg = atm2veg_a
        else:
            # natural ocean-to-atmosphere and atmosphere to ocean
            sfc2atm = sfc2atm_n
            atm2sfc = atm2sfc_n
            veg2atm = veg2atm_n
            atm2veg = atm2veg_n
        
        # adjust ocean-atmosphere exchange
        surface_ocean_change -= sfc2atm
        atmosphere_change += sfc2atm
        surface_ocean_change += atm2sfc
        atmosphere_change -= atm2sfc
        
        # adjust respiration and photosynthesis
        vegetation_change -= veg2atm
        atmosphere_change += veg2atm
        vegetation_change += atm2veg
        atmosphere_change -= atm2veg
        
            
        atmosphere[ii] = atmosphere[ii-1] + atmosphere_change
        fuel_reserves[ii] = fuel_reserves[ii-1] + fuel_reserves_change
        vegetation[ii] = vegetation[ii-1] + vegetation_change
        deep_ocean[ii] = deep_ocean[ii-1] + deep_ocean_change
        soil[ii] = soil[ii-1] + soil_change
        permafrost[ii] = permafrost[ii-1] + permafrost_change
        surface_ocean[ii] = surface_ocean[ii-1] + surface_ocean_change
        marine_biota[ii] = marine_biota[ii-1] + marine_biota_change
        dissolved_organic[ii] = dissolved_organic[ii-1] + dissolved_organic_change
        
    total_change = (atmosphere_change +
                    fuel_reserves_change +
                    vegetation_change +
                    deep_ocean_change +
                    soil_change +
                    permafrost_change +
                    surface_ocean_change +
                    marine_biota_change +
                    dissolved_organic_change)
    ax0.plot(atmosphere, color='turquoise')
    ax0.text(0, atmosphere[0], 'atmosphere', color='turquoise', va='top')
    ax0.plot(fuel_reserves, color='black')
    ax0.text(0, fuel_reserves[0], 'coal, oil, and gas reserves', color='black', va='top')
    ax0.plot(vegetation, color='forestgreen')
    ax0.text(0, vegetation[0], 'vegetation', color='forestgreen', va='top')
    ax0.plot(np.array(deep_ocean)-deep_ocean_0, color='navy')
    ax0.text(0, 0, r'deep ocean change', color='navy')
    ax0.plot(soil, color='brown')
    ax0.text(0, soil[0]+20, 'soil', color='brown')
    ax0.plot(permafrost,color='darkseagreen')
    ax0.text(0, permafrost[0], 'permafrost', color='darkseagreen', va='top')
    ax0.plot(surface_ocean, color='royalblue')
    ax0.text(0, surface_ocean[0], 'surface ocean', color='royalblue', va='top')
    ax0.plot(marine_biota, color='tan')
    ax0.text(0, marine_biota[0], 'marine biota', color='tan', va='top')
    ax0.plot(dissolved_organic, color='gray')
    ax0.text(0, dissolved_organic[0], 'dissolved organic', color='gray', va='top')
    #ax0.set_yscale('log')
    #ax0.set_ylim(300, 4000)
    ax0.set_ylabel(r'Petagrams Carbon (PgC), or 10$^{15}$g')
    ax0.set_xlabel('simulation year')
    ax0.set_title('Carbon reservoirs over time')
    
    img = mpimg.imread('ccycle_drawing.png')
    ax1.imshow(img, aspect='equal')
    ax1.set_axis_off()
    base_width=5
    headwidth=14
            
    flux_arrow(ax1, 307, 201, 0, 244, atm2sfc, atm2sfc_n) # atmos -> ocean
    flux_arrow(ax1, 368, 470, 0, -244, sfc2atm, sfc2atm_n) # ocean -> atmos
    flux_arrow(ax1, 251, 545, 0, 60, sfc2deep, sfc2deep_n) # surface -> deep
    flux_arrow(ax1, 277, 625, 0, -60, deep2sfc, deep2sfc_n) # deep -> surface
    flux_arrow(ax1, 264, 686, 0, 56, deep2rock, deep2rock_n) # deep to floor
    flux_arrow(ax1, 350, 510, 38, 0, sfc2bio, sfc2bio_n) # surface ocean -> marine biota
    flux_arrow(ax1, 410, 530, -38, 0, bio2sfc, bio2sfc_n) # marine biota -> surface ocean
    flux_arrow(ax1, 414, 548, -94, 75, bio2deep, bio2deep_n) # marine biota -> deep sea
    flux_arrow(ax1, 447, 551, 0,74, bio2doc, bio2doc_n) # marine biota -> DOC
    flux_arrow(ax1, 400, 667, -91, 0, doc2deep, doc2deep_n) # DOC -> deep sea
    flux_arrow(ax1, 546, 546, -34, 0, rvr2sea, rvr2sea_n) # river emptying
    flux_arrow(ax1, 635, 543, 0, 27, burial, burial_n) # river burial
    flux_arrow(ax1, 627, 521, 0, -380, rivr2atm, rivr2atm_n) # river outgassing
    flux_arrow(ax1, 905, 192, 0, 250, atm2veg, atm2veg_n) # photosynthesis
    flux_arrow(ax1, 984, 460, 0, -250, veg2atm, veg2atm_n) # respiration
    flux_arrow(ax1, 1050, 227, 0, -100, volc_n, volc_n) # volcanism
    flux_arrow(ax1, 1147, 180, 0, 256, atm2rivr, atm2rivr_n) # wind weathering
    flux_arrow(ax1, 1147, 476, -40, -20, rock2rivr, rock2rivr_n) # stream weathering
    flux_arrow(ax1, 864, 445, -20, 0, soil2rivr, soil2rivr_n) # soil export to rivers weathering
    if humans:
        ax1.arrow(758, 521, 0, -380, width=base_width, head_width=headwidth, ec='red', fc='red') # emissions
        ax1.arrow(820, 431, 0, -290, width=base_width, head_width=headwidth, ec='red', fc='red') # net land use change
    
    net_up_arrow(ax1, 339, 170, -55, sfc2atm-atm2sfc, sfc2atm_n-atm2sfc_n) # net ocean -> atmos
    net_up_arrow(ax1, 951, 148, -23, veg2atm-atm2veg, veg2atm_n-atm2veg_n) # net photo/resp
    
    ax1.set_title('Carbon fluxes compared to pre-industrial at year 200.')

b_update = widgets.Button(description='update')
b_reset = widgets.Button(description='reset to defaults')
human_radio = widgets.RadioButtons(value='pre-industrial', options=['pre-industrial', 'modern'])
#human_checkbox = widgets.Checkbox(description='on', value=False)
ocean_down_checkbox = widgets.Checkbox(description=r'$\downarrow$ (dissolution)', value=False)
ocean_up_checkbox = widgets.Checkbox(description=r'$\uparrow$ (outgassing)', value=False)
veg_up_checkbox = widgets.Checkbox(description=r'$\uparrow$ (respiration)', value=False)
veg_down_checkbox = widgets.Checkbox(description=r'$\downarrow$ (photosynthesis)', value=False)
#propo_checkbox = widgets.Checkbox(description='changing', value=False)
propo_radio = widgets.RadioButtons(value='constant', options=['constant', 'variable'])

output = widgets.Output()
with output:
    fig = plt.figure(figsize=(12,7))
    spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[1, 3], wspace=0, hspace=0)
    ax0 = fig.add_subplot(spec[0])
    ax1 = fig.add_subplot(spec[1])
    
def clear_boxes(b):
    human_radio.value='pre-industrial'
    ocean_down_checkbox.value=False
    ocean_up_checkbox.value=False
    veg_up_checkbox.value=False
    veg_down_checkbox.value=False
    propo_radio.value='constant'
    
def update_plot(b):
    with output:
        ax0.cla()  
        ax1.cla()  
        #[l.remove() for l in ax0.artists]
        #[l.remove() for l in ax1.artists]
        #[l.remove() for l in ax0.lines]
        #[l.remove() for l in ax1.lines]
        #[t.remove() for t in ax0.texts]
        #[t.remove() for t in ax1.texts]
        run_model(ax0, ax1, humans=human_radio.value=='modern', 
                n_iterations = 200, 
                buffered_up_ocn=ocean_up_checkbox.value, 
                buffered_down_ocn=ocean_down_checkbox.value, 
                buffered_up_veg=veg_up_checkbox.value, 
                buffered_down_veg=veg_down_checkbox.value,
                proportionate=propo_radio.value=='variable')

update_plot(None)
b_update.on_click(update_plot)
b_reset.on_click(clear_boxes)

humanbox = widgets.VBox([widgets.Label('Emissions'), human_radio])
oceanbox = widgets.VBox([widgets.Label('Connect Ocean-Atmos'), ocean_down_checkbox, ocean_up_checkbox])
veggiebox = widgets.VBox([widgets.Label('Connect Bio-Atmos'), veg_down_checkbox, veg_up_checkbox])
propobox = widgets.VBox([widgets.Label('Other fluxes'), propo_radio])
controlboxes = widgets.HBox([humanbox, oceanbox, veggiebox, propobox])
controls = widgets.VBox([controlboxes, b_update, b_reset])
# widgets.VBox([output, controls]) # for some reason this works better in the notebook
