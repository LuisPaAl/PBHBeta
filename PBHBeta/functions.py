# File: functions.py
## Module with functions
### Version BETA

from scipy.optimize import fsolve
from scipy.optimize import least_squares
from scipy.integrate import solve_ivp
from numpy import diff
import sys
from scipy import special
from PBHBeta import constants
from PBHBeta import constraints
import numpy as np

def put_M_array(Mass_min, Mass_max):
    """
    Generate an array of primordial black hole (PBH) masses in grams based on specified limits.

    Parameters:
        Mass_min (float): The minimum PBH mass value in grams.
        Mass_max (float): The maximum PBH mass value in grams.

    Returns:
        np.ndarray: An array of calculated PBH masses.
    """
    i = 0
    M = 0
    delta_M = 0.0123
    M_tot_try = []
    num_values = 20

    mass_array = np.geomspace(Mass_min, 10**(i*delta_M) , num_values)

    while M < constraints.data_mass[0]:
        M = 10**(i*delta_M)
        M_tot_try.append(M)
        i = i+1

    M_tot_try = np.concatenate((mass_array, M_tot_try, constraints.data_mass))
    M_tot_try = np.unique(M_tot_try)
    M = M_tot_try[-1]

    A = M
    j = 0

    while M < Mass_max:
        j = j+1
        M = A*10**(j*delta_M)
        M_tot_try = np.append(M_tot_try,[M])

    constraints.M_tot = np.array(M_tot_try)

    return constraints.M_tot


def diff_rad_rel(ln_rho,initial,M,beta0):

    """In the scenario where PBHs evaporate before reaching the energy scale of interest (as is the case, for example,
    before reaching the energy scale of BBN), we calculate the PBH abundance by assuming the existence of remnants with
    a mass equal to the Planck mass. Instead of simultaneously solving Eqs.(10) and (11) with the constraint Eq. (8), we
    focus on solving Eq.(10) with the constraint $\Omega_{PBH} = (m_{Pl}/M_{PBH})\beta(M_{PBH})$."""

    # Extract initial scale factor b and calculate Om_0
    b = initial[0]
    Om_0 = beta0 * b * (constants.M_pl_g / M)

    # Calculate the derivative of the scale factor b
    dy = -(Om_0 - 1.) * b / (Om_0 - 4.)

    return dy


def diff_rad(ln_rho,initial,M,beta0):
    """This function corresponds to Eqs.(10) and (11) with the constraint Eq.(8) in our reference paper. It is employed
    to calculate the abundance of PBHs in a radiation-dominated universe as a function of total energy density."""

    # Initialize dy array
    dy = np.zeros(initial.shape)

    # Extract initial values of scale factor b and time
    b = initial[0]
    time = initial[1]

    # Calculate Delta_t and Om_0
    Delta_t = constants.t_pl * (M / constants.M_pl_g) ** 3
    Om_0 = beta0 * b * (1. - time / Delta_t) ** (1. / 3)

    # Calculate the derivative of the scale factor b and the time derivative of the density of radiation
    dy[0] = -(Om_0 - 1.) * b / (Om_0 - 4.)
    dy[1] = 3 ** (1. / 2) * constants.M_pl / ((Om_0 - 4.) * np.exp(ln_rho) ** (1. / 2))

    return dy


def end_evol(ln_rho,initial,M,beta0):
    """This function is used to determine whether a PBH reaches the Planck mass (thus becoming a Planck relic) or not.
    By solving the system of equations (10) and (11) with the constraint (8) from our reference article, this function
    is used as a stopping condition for the evolution of the system. In the event that the evolution is halted before
    reaching the desired energy scale (such as the scale of BBN), the evolution of PBHs is carried out considering them
    as Planck mass relics."""
    # Calculate Delta_t and Mass_end
    Delta_t = constants.t_pl * (M / constants.M_pl_g) ** 3
    Mass_end = M * (1. - diff_rad(ln_rho,initial,M,beta0)[1] / Delta_t) ** (1. / 3)

    # Return the difference between the final mass of a system and the Planck mass
    return Mass_end - constants.M_pl_g


def k_end_over_k(Mpbh, omega):
    """
    Calculates the ratio of k_end/k for a given PBH mass and radiation energy density parameter.

    Parameters:
        - Mpbh (float): The mass of the PBH, in grams.
        - omega (float): The energy density parameter for radiation.

    Returns:
        - ratio (float): The ratio of k_end/k for the given PBH mass and radiation energy density parameter.
    """
    # Calculate the exponent for the ratio of k_end/k
    exp = (1 + 3 * omega) / (3 * (1 + omega))

    # Calculate the ratio of k_end/k using the given formula
    ratio = (Mpbh * constants.H_end / (constants.gam_rad * 3 * constants.M_pl)) ** exp

    return ratio


def rho_f(Mpbh, omega):
    """
    Calculates the final density of black holes after evaporation.

    Parameters:
        - Mpbh (float): The initial mass of a black hole, in grams.
        - omega (float): The ratio of the energy density of dark matter to the critical density of the universe.

    Returns:
        - rho (float): The final density of black holes, in grams per cubic centimeter.
    """
    # Calculate the exponent for the final density
    exp = (6 * (1 + omega)) / (1 + (3 * omega))

    # Calculate the final density using the given formula and the k_end_over_k function
    rho = constants.rho_end_inf / (k_end_over_k(Mpbh,omega)) ** exp

    return rho

####calcular betas es una funcion que unicamente debe
####depender de la masa

ln_den_end = np.log(constants.rho_end)


		
def Betas_DM(M_tot):

    """
    Calculates the abundance of PBHs for dark matter constraints. See equations (13) and (19)

    Parameters:
        - M_tot (array-like): Array of masses in grams.

    Returns:
        A tuple containing four numpy arrays:
            - M_n (numpy.ndarray): Represents the masses of PBHs can be considered candidates for Dark Matter (DM).
            - beta (numpy.ndarray): Corresponds to the abundance obtained from M_n.
            - M_relic (numpy.ndarray): Masses of the relic dark matter components.
            - beta_relic_prim (numpy.ndarray): Corresponds to abundance obtained from M_relic.
    """

    M_n = []
    betas_prim = []
    M_relic = []
    betas_relic_prim = []

    for i in range(len(M_tot)):
        if M_tot[i] > 4.1*10**14:
            M_n.append(M_tot[i])
            beta = 1.86*10**-18*(M_tot[i]/(10**15))**(1/2)
            betas_prim.append(beta)
        elif M_tot[i] < 10**11*constants.M_pl_g:
            M_relic.append(M_tot[i])
            beta = 2*10**-28*(M_tot[i]/constants.M_pl_g)**(3/2)
            betas_relic_prim.append(beta)
        else:
            beta = constants.ev1
        constraints.betas_DM_tot.append(beta/constants.gam_rad**(1/2))
    
    betas_prim = np.array(betas_prim)
    betas_relic_prim = np.array(betas_relic_prim)
    M_n = np.array(M_n)
    M_relic = np.array(M_relic)
    betas = betas_prim/constants.gam_rad**(1/2)
    betas_relic = betas_relic_prim/constants.gam_rad**(1/2)

    return M_n, betas, M_relic, betas_relic

    
def Betas_BBN(M_tot, omega):
    """
    Calculates the beta parameters and relic abundances for dark matter particles formed during BBN.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.
        - omega (float): The baryon-to-photon ratio.

    Returns:
        - M_bbn (numpy.ndarray): The masses of dark matter particles formed during BBN, in solar masses.
        - betas_bbn (numpy.ndarray): The corresponding beta parameter values for the dark matter particles formed during BBN.
        - M_bbn_bbn (numpy.ndarray): The masses of dark matter particles formed only during BBN, in solar masses.
        - M_bbn_pbbn (numpy.ndarray): The masses of dark matter particles formed both during and after BBN, in solar masses.
        - Omegas_bbn (numpy.ndarray): The relic abundances of dark matter particles formed only during BBN.
        - Omegas_bbn_pbbn (numpy.ndarray): The relic abundances of dark matter particles formed both during and after BBN.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
    """

    betas_bbn = []
    M_bbn = []
    M_bbn_bbn = []
    Omegas_bbn = []
    Omegas_bbn_pbbn = []
    M_bbn_pbbn = []

    rho_form_rad = rho_f(M_tot, omega)
    j = 0
    
    for i in range(len(M_tot)):
        if M_tot[i]>= constraints.data_mass[0] and M_tot[i]<constraints.data_mass[76]:
            M_bbn.append(M_tot[i])
            beta = constraints.data_abundances[j]/constants.gam_rad**(1/2)
            betas_bbn.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            if sol_try.t[-1] > ln_den_end:
                sol_try = solve_ivp(diff_rad_rel,(ln_den_f,ln_den_end),np.array([1.]),t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
                y = beta*sol_try.y[0][-1]*(constants.M_pl_g/M_tot[i])
                Omegas_bbn_pbbn.append(y)
                M_bbn_pbbn.append(M_tot[i])
            else:
                Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
                y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
                Omegas_bbn.append(y)
                M_bbn_bbn.append(M_tot[i])
            j = j+1
        elif M_tot[i]>= constraints.data_mass[76] and M_tot[i]<2.5*10**13:
            M_bbn.append(M_tot[i])
            beta = constraints.data_abundances[76]/constants.gam_rad**(1/2)
            betas_bbn.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_bbn.append(y)
            M_bbn_bbn.append(M_tot[i])
            j = j+1
        else:
            beta = constants.ev1
            y = constants.ev2
        constraints.betas_BBN_tot.append(beta)
        constraints.Omega_BBN_tot.append(y)
    
    betas_bbn = np.array(betas_bbn)
    M_bbn = np.array(M_bbn)
    M_bbn_bbn = np.array(M_bbn_bbn)
    M_bbn_pbbn = np.array(M_bbn_pbbn)
    Omegas_bbn = np.array(Omegas_bbn)
    Omegas_bbn_pbbn = np.array(Omegas_bbn_pbbn)
    
    return M_bbn, betas_bbn, M_bbn_bbn, M_bbn_pbbn, Omegas_bbn, Omegas_bbn_pbbn


def Betas_SD(M_tot, omega):
    """
    Calculates the beta parameters and relic abundances for self-destructive dark matter particles.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.
        - omega (float): The baryon-to-photon ratio.

    Returns:
        - M_sd (numpy.ndarray): The masses of self-destructive dark matter particles, in solar masses.
        - betas_sd (numpy.ndarray): The corresponding beta parameter values for the self-destructive dark matter particles.
        - M_sd_bbn (numpy.ndarray): The masses of self-destructive dark matter particles formed during BBN, in solar masses.
        - Omegas_sd (numpy.ndarray): The relic abundances of self-destructive dark matter particles formed during BBN.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
        - The self-destruction process is assumed to be due to radiative decay, with a decay constant of 10^(-21)/gamma_rad^(1/2).
        - The function only considers self-destructive dark matter particles with masses between 10^11 and 10^13 solar masses.
        - The relic abundances are calculated using the DOP853 solver from the Scipy library.
    """
    
    betas_sd = []
    M_sd = []
    M_sd_bbn = []
    Omegas_sd = []
    
    rho_form_rad = rho_f(M_tot, omega)

    for i in range(len(M_tot)):
        if M_tot[i]> 10**11 and M_tot[i]<10**13:
            M_sd.append(M_tot[i])
            beta = 10**(-21)/constants.gam_rad**(1/2)
            betas_sd.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_sd.append(y)
            M_sd_bbn.append(M_tot[i])
        else:
            beta = constants.ev1
            y = constants.ev2
        constraints.betas_SD_tot.append(beta)
        constraints.Omega_SD_tot.append(y)
    
    betas_sd = np.array(betas_sd)
    M_sd = np.array(M_sd)
    M_sd_bbn = np.array(M_sd_bbn)
    Omegas_sd = np.array(Omegas_sd)
    
    return M_sd, betas_sd, M_sd_bbn, Omegas_sd



def Betas_CMB_AN(M_tot, omega):
    """
    Calculates the beta parameters and relic abundances for dark matter particles formed during CMB-era annihilation.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.
        - omega (float): The present-day density of baryons relative to the critical density.

    Returns:
        - M_an (numpy.ndarray): The masses of dark matter particles formed during CMB-era annihilation, in solar masses.
        - betas_an (numpy.ndarray): The corresponding beta parameter values for the dark matter particles formed during CMB-era annihilation.
        - M_an_bbn (numpy.ndarray): The masses of dark matter particles formed during CMB-era annihilation and BBN, in solar masses.
        - Omegas_an (numpy.ndarray): The relic abundances of dark matter particles formed during CMB-era annihilation.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
        - This function assumes that dark matter annihilation began during the CMB era, and ignores any effects from earlier times.
        - The beta parameter values and relic abundances are calculated assuming the "slow-rollover" approximation for freeze-out.
    """

    betas_an = []
    M_an = []
    M_an_bbn = []
    Omegas_an = []
    
    rho_form_rad = rho_f(M_tot, omega)

    for i in range(len(M_tot)):
        if M_tot[i]> 2.5*10**13 and M_tot[i]<2.4*10**14:
            M_an.append(M_tot[i])
            beta = 3*10**(-30)*(M_tot[i]/10**13)**3.1/constants.gam_rad**(1/2)
            betas_an.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_an.append(y)
            M_an_bbn.append(M_tot[i])
        else:
            beta = constants.ev1
            y = constants.ev2
        constraints.betas_CMB_AN_tot.append(beta)
        constraints.Omega_CMB_AN_tot.append(y)
    
    betas_an = np.array(betas_an)
    M_an = np.array(M_an)
    M_an_bbn = np.array(M_an_bbn)
    Omegas_an = np.array(Omegas_an)
    
    return M_an, betas_an, M_an_bbn, Omegas_an


def Betas_GRB(M_tot, omega):
    """
    Calculates the beta parameters and relic abundances for dark matter particles formed during the GRB epoch.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.
        - omega (float): The baryon-to-photon ratio.
    
    Returns:
        - M_grb1 (numpy.ndarray): The masses of dark matter particles formed during the first GRB epoch, in solar masses.
        - M_grb2 (numpy.ndarray): The masses of dark matter particles formed during the second GRB epoch, in solar masses.
        - betas_grb1 (numpy.ndarray): The corresponding beta parameter values for the dark matter particles formed during the first GRB epoch.
        - betas_grb2 (numpy.ndarray): The corresponding beta parameter values for the dark matter particles formed during the second GRB epoch.
        - M_grb1_bbn (numpy.ndarray): The masses of dark matter particles formed during the first GRB epoch and BBN, in solar masses.
        - M_grb2_bbn (numpy.ndarray): The masses of dark matter particles formed during the second GRB epoch and BBN, in solar masses.
        - Omegas_grb1 (numpy.ndarray): The relic abundances of dark matter particles formed during the first GRB epoch.
        - Omegas_grb2 (numpy.ndarray): The relic abundances of dark matter particles formed during the second GRB epoch.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
        - The function uses numerical integration to calculate the relic abundances.
        - The values for beta and relic abundance for M_tot outside the range (3e13, 7e16) solar masses are set to constants.ev1 and constants.ev2 respectively.
    """

    betas_grb1 = []
    M_grb1 = []
    betas_grb2 = []
    M_grb2 = []

    M_grb1_bbn = []
    Omegas_grb1 = []
    M_grb2_bbn = []
    Omegas_grb2 = []
    
    rho_form_rad = rho_f(M_tot, omega)

    for i in range(len(M_tot)):
        if M_tot[i]> 3*10**13 and M_tot[i]<4.1*10**14:
            M_grb1.append(M_tot[i])
            beta = 5*10**(-28)*(M_tot[i]/(4.1*10**14))**-3.3/constants.gam_rad**(1/2)
            betas_grb1.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_grb1.append(y)
            M_grb1_bbn.append(M_tot[i])
        
        elif M_tot[i]> 4.1*10**14 and M_tot[i]<7*10**16:
            M_grb2.append(M_tot[i])
            beta = 5*10**(-26)*(M_tot[i]/(4.1*10**14))**3.9/constants.gam_rad**(1/2)
            betas_grb2.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_grb2.append(y)
            M_grb2_bbn.append(M_tot[i])
        else:
            beta = constants.ev1
            y = constants.ev2
        constraints.betas_GRB_tot.append(beta)
        constraints.Omega_GRB_tot.append(y)
    
    betas_grb1 = np.array(betas_grb1)
    M_grb1 = np.array(M_grb1)
    betas_grb2 = np.array(betas_grb2)
    M_grn2 = np.array(M_grb2)
    M_grb1_bbn = np.array(M_grb1_bbn)
    Omegas_grb1 = np.array(Omegas_grb1)
    M_grb2_bbn = np.array(M_grb2_bbn)
    Omegas_grb2 = np.array(Omegas_grb2)

    
    return M_grb1, M_grb2, betas_grb1, betas_grb2, M_grb1_bbn, M_grb2_bbn, Omegas_grb1, Omegas_grb2

def Betas_Reio(M_tot, omega):

    """
    Calculates the beta parameters and relic abundances for dark matter particles formed during reionization epoch.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.
        - omega (float): The baryon-to-photon ratio.

    Returns:
        - M_reio (numpy.ndarray): The masses of dark matter particles formed during reionization epoch, in solar masses.
        - betas_reio (numpy.ndarray): The corresponding beta parameter values for the dark matter particles formed during reionization epoch.
        - M_reio_bbn (numpy.ndarray): The masses of dark matter particles formed during reionization epoch and BBN, in solar masses.
        - Omegas_reio (numpy.ndarray): The relic abundances of dark matter particles formed during reionization epoch.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
        - The function uses numerical integration to calculate the relic abundances.
        - The values for beta and relic abundance for M_tot outside the range (1e15, 1e17) solar masses are set to constants.ev1 and constants.ev2 respectively.
    """
    betas_reio = []
    M_reio = []

    M_reio_bbn = []
    Omegas_reio = []
    
    rho_form_rad = rho_f(M_tot, omega)

    for i in range(len(M_tot)):
        if M_tot[i]> 10**15 and M_tot[i]<10**17:
            M_reio.append(M_tot[i])
            beta = 2.4*10**(-26)*(M_tot[i]/(4.1*10**14))**4.3/constants.gam_rad**(1/2)
            betas_reio.append(beta)
        
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
            y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
            Omegas_reio.append(y)
            M_reio_bbn.append(M_tot[i])
        else:
            beta = constants.ev1
            y = constants.ev2
        constraints.betas_Reio_tot.append(beta)
        constraints.Omega_Reio_tot.append(y)
    
    betas_reio = np.array(betas_reio)
    M_reio = np.array(M_reio)
    M_reio_bbn = np.array(M_reio_bbn)
    Omegas_reio = np.array(Omegas_reio)
    
    return M_reio, betas_reio, M_reio_bbn, Omegas_reio

def Betas_LSP(M_tot):
    """
    Calculates the beta parameters for dark matter particles in the lightest supersymmetric particle (LSP) scenario.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.

    Returns:
        - M_lsp (numpy.ndarray): The masses of dark matter particles in the LSP scenario, in solar masses.
        - betas_lsp (numpy.ndarray): The corresponding beta parameter values for dark matter particles in the LSP scenario.

    Notes:
        - The function assumes that the total mass of dark matter consists of only one type of particle.
        - The returned arrays are sorted in increasing order of mass.
        - The values for beta for M_tot outside the range (0, 1e11) solar masses are set to constants.ev1.
    """

    betas_lsp = []
    M_lsp = []
    
    for i in range(len(M_tot)):
        if M_tot[i]< 10**11:
            M_lsp.append(M_tot[i])
            beta = 10**(-18)*(M_tot[i]/(10**11))**(-1/2)/constants.gam_rad**(1/2)
            betas_lsp.append(beta)
        else:
            beta = constants.ev1
        constraints.betas_LSP_tot.append(beta)
    
    betas_lsp = np.array(betas_lsp)
    M_lsp = np.array(M_lsp)
    
    return M_lsp, betas_lsp

def Omegas_LSP(M_tot, omega):
    M_lsp_bbn = []
    Omegas_lsp = []
    M_lsp_pbbn = []
    Omegas_lsp_pbbn = []
    M_tot = np.array(M_tot)
    
    rho_form_rad = rho_f(M_tot, omega)
    
    for i in range(len(M_tot)):
        if M_tot[i]<1e11:
            beta = 1e-18*(M_tot[i]/1e11)**(-1/2)/constants.gam_rad**(1/2)
            ln_den_f = np.log(rho_form_rad[i])
            if ln_den_f <= ln_den_end:
                continue
            ln_den = np.linspace(ln_den_f,ln_den_end,10000)
            sol_try = solve_ivp(diff_rad,(ln_den_f,ln_den_end),np.array([1.,0.]),events=end_evol,t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
            if sol_try.t[-1] > ln_den_end:
                sol_try = solve_ivp(diff_rad_rel,(ln_den_f,ln_den_end),np.array([1.]),t_eval=ln_den,args=(M_tot[i],beta),method = "DOP853")
                y = beta*sol_try.y[0][-1]*(constants.M_pl_g/M_tot[i])
                Omegas_lsp_pbbn.append(y)
                M_lsp_pbbn.append(M_tot[i])
            else:
                Delta_t = constants.t_pl*(M_tot[i]/constants.M_pl_g)**3
                y = beta*sol_try.y[0][-1]*(1.-sol_try.y[1][-1]/Delta_t)**(1./3)
                Omegas_lsp.append(y)
                M_lsp_bbn.append(M_tot[i])
        else:
            y = constants.ev2
            constraints.Omega_LSP_tot.append(y)
            
    M_lsp_bbn = np.array(M_lsp_bbn)
    Omegas_lsp = np.array(Omegas_lsp)
    M_lsp_pbbn = np.array(M_lsp_pbbn)
    Omegas_lsp_pbbn = np.array(Omegas_lsp_pbbn)
    return M_lsp_bbn, Omegas_lsp, M_lsp_pbbn, Omegas_lsp_pbbn

def get_Betas_full(M_tot):

    """
    Calculates the minimum beta parameter value for each dark matter particle mass using all available constraints.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.

    Returns:
        - betas_full (numpy.ndarray): The minimum beta parameter value for each dark matter particle mass.

    Notes:
        - The function calculates the minimum beta parameter value for each dark matter particle mass by comparing the beta parameter values obtained from different astrophysical constraints: DM halos, BBN, self-interaction, CMB, GRBs, reionization, and LSP.
    """
    DM_tot = np.array(constraints.betas_DM_tot)
    BBN_tot = np.array(constraints.betas_BBN_tot)
    SD_tot = np.array(constraints.betas_SD_tot)
    CMB_tot = np.array(constraints.betas_CMB_AN_tot)
    GRB_tot = np.array(constraints.betas_GRB_tot)
    Reio_tot = np.array(constraints.betas_Reio_tot)
    LSP_tot = np.array(constraints.betas_LSP_tot)
    constraints.betas_full = M_tot*0
    for i in range(len(M_tot)):
        constraints.betas_full[i] = min(DM_tot[i], BBN_tot[i], SD_tot[i], CMB_tot[i], GRB_tot[i], Reio_tot[i], LSP_tot[i])
    return constraints.betas_full


def get_Omegas_full(M_tot):

    """
    Calculates the minimum Omega parameter value for each dark matter particle mass using all available constraints.

    Parameters:
        - M_tot (array-like): The total mass of dark matter, in units of solar masses.

    Returns:
        - Omegas_full (numpy.ndarray): The minimum beta parameter value for each dark matter particle mass.

    Notes:
        - The function calculates the minimum Omega parameter value for each dark matter particle mass by comparing the beta parameter values obtained from different astrophysical constraints: DM halos, BBN, self-interaction, CMB, GRBs, reionization, and LSP.
    """
    DM_tot = np.array(constraints.Omega_DM_tot)
    BBN_tot = np.array(constraints.Omega_BBN_tot)
    SD_tot = np.array(constraints.Omega_SD_tot)
    CMB_tot = np.array(constraints.Omega_CMB_AN_tot)
    GRB_tot = np.array(constraints.Omega_GRB_tot)
    Reio_tot = np.array(constraints.Omega_Reio_tot)
    LSP_tot = np.array(constraints.Omega_LSP_tot)
    constraints.Omegas_full = M_tot*0
    for i in range(len(M_tot)):
        constraints.Omegas_full[i] = min(DM_tot[i], BBN_tot[i], SD_tot[i], CMB_tot[i], GRB_tot[i], Reio_tot[i], LSP_tot[i])
    return constraints.Omegas_full

def inverse_error(betas, delta_c):
    aux = []
    for i in range(len(betas)):
        aux.append(delta_c/(np.sqrt(2)*special.erfcinv(betas[i])))
    return aux

def a_endre(rho_r0, rho_end_re):
    return (rho_r0 / rho_end_re) ** (1. / 4)

def k_rad(M):
    a_end_inf_rad = (constants.rho_r0 / constants.rho_end_inf) ** (1. / 4)
    k_end = a_end_inf_rad * constants.H_end
    k_end_over_k_rad = (M/(7.1*10**-2*constants.gam_rad*(1.8*10**15/constants.H_end)))**(1/2)
    k = (k_end/k_end_over_k_rad)*constants.GeV*constants.metter_m1
    k = np.array(k)
    return k