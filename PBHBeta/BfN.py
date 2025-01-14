# File: BfN.py
## Module with BfN to compute
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

# Set the values of the variables
rho_end_inf =  constants.rho_end_inf #define rho_end_inf
H_end = constants.H_end #define H_end
gam_rad = constants.gam_rad
rho_end = constants.rho_end # define rho_end
M_pl_g = constants.M_pl_g # define M_pl_g
ln_den_end = np.log(constants.rho_end)
t_pl_s = constants.t_pl_s # s
s_to_evm1 = constants.s_to_evm1
t_pl = constants.t_pl
M_pl = constants.M_pl
ev1 = constants.ev1
ev2 = constants.ev2
rho_end = constants.rho_end
log10_M_tot = np.linspace(0,20,1000)
ln_den_end = np.log(rho_end)

def get_betas_reh_tot(N_re, omega, gam_reh):
    """
    Calculates the values of betas_reh_tot for a given set of parameters.

    Parameters:
        - N_re (float): The number of efolds during reheating.
        - omega (float): The equation of state parameter during reheating.
        - gam_reh (float): The ratio of the radiation energy density to the inflaton energy density at the end of reheating..
    Returns:
        - betas_reh_tot (list): A list of values of betas_reh_tot.
    Raises:
        - ValueError: If the end of reheating happens after BBN.
    """
    M_tot = np.array(constraints.M_tot)# define M_tot
    betas_full = np.array(constraints.betas_full)# define betas_full
    Omegas_full = np.array(constraints.data_Omegas_full)# define Omegas_full


    # Calculate k_end_over_k_reh and rho_form_reh
    k_end_over_k_reh = (M_tot/(7.1*10**-2*gam_reh*(1.8*10**15/H_end)))**(1/3)
    rho_form_reh = rho_end_inf/(k_end_over_k_reh)**6
    ln_rho_form_reh = np.log(rho_form_reh)

    # Calculate rho_end_reh and check if it's after BBN
    rho_end_reh = rho_end_inf*np.exp(-3*N_re)
    if rho_end_reh <= rho_end:
        raise ValueError("The end of reheating happens after BBN")
    ln_den_end_reh = np.log(rho_end_reh)

    # Create an empty list to store the values of betas_reh_tot_50
    betas_reh_tot = []

    # Loop over the values of M_tot
    for i in range(len(M_tot)):
        end_value = Omegas_full[i]
        M = M_tot[i]
        ln_den_f = np.log(rho_form_reh[i])
        
        def diff_rad_rel(ln_rho,initial,M,beta0):
            b = initial[0]
            Om_0 = beta0*b*(constants.M_pl_g/M)
            dy = -(Om_0-1.)*b/(Om_0-4.)
            return dy
        
        def diff_rad(ln_rho,initial,M,beta0):
            dy = np.zeros(initial.shape)
            b = initial[0]
            time = initial[1]
            Delta_t = constants.t_pl*(M/constants.M_pl_g)**3
            Om_0 =  beta0*b*(1.-time/Delta_t)**(1./3)
            dy[0] = -(Om_0-1.)*b/(Om_0-4.)
            dy[1] = 3**(1./2)*constants.M_pl/((Om_0-4.)*np.exp(ln_rho)**(1./2))
            return dy
            
        def end_evol(ln_rho,initial,M,beta0):
            Delta_t = t_pl*(M/M_pl_g)**3
            Mass_end = M*(1.-diff_rad(ln_rho,initial,M,beta0)[1]/Delta_t)**(1./3)
            return Mass_end-M_pl_g
        
        def diff_ext_rel(ln_rho,initial,M,beta0,omega):
            dy = np.zeros(initial.shape)
            b = initial[0]
            Om_ext = initial[1]
            Om_0 = beta0*b*(M_pl_g/M)
            dy[0] = -(Om_0+(1-3*omega)*Om_ext-1.)*b/(Om_0+(1-3*omega)*Om_ext-4.)
            dy[1] = -(Om_0+(1-3*omega)*Om_ext+3*omega-1)*Om_ext/(Om_0+(1-3*omega)*Om_ext-4)
            return dy
            
        def diff_ext(ln_rho,initial,M,beta0,omega):
            dy = np.zeros(initial.shape)
            b = initial[0]
            time = initial[1]
            Om_ext = initial[2]
            Delta_t = t_pl*(M/M_pl_g)**3
            Om_0 =  beta0*b*(1.-time/Delta_t)**(1./3)
            dy[0] = -(Om_0+(1-3*omega)*Om_ext-1.)*b/(Om_0+(1-3*omega)*Om_ext-4.)
            dy[1] = 3**(1./2)*M_pl/((Om_0+(1-3*omega)*Om_ext-4.)*np.exp(ln_rho)**(1./2))
            dy[2] = -(Om_0+(1-3*omega)*Om_ext+3*omega-1)*Om_ext/(Om_0+(1-3*omega)*Om_ext-4)
            return dy
            
        def end_evol_ext(ln_rho,initial,M,beta0,omega):
            Delta_t = t_pl*(M/M_pl_g)**3
            Mass_end = M**(1.-diff_ext(ln_rho,initial,M,beta0,omega)[1]/Delta_t)**(1./3)
            return Mass_end - M_pl_g
        
        def objective_reh(beta0):
            initial_reh = np.array([1.,0.,1.-beta0[0]])
            sol_reh = solve_ivp(diff_ext,(ln_den_f,ln_den_end_reh),initial_reh,t_eval=ln_den_reh,args=(M,beta0[0],omega),method = "DOP853")
            initial = np.array([sol_reh.y[0][-1],sol_reh.y[1][-1]])
            sol = solve_ivp(diff_rad,(ln_den_end_reh,ln_den_end),initial,t_eval=ln_den,args=(M,beta0[0]),method = "DOP853")
            Delta_t = t_pl*(M/M_pl_g)**3
            y = beta0[0]*sol.y[0]*(1.-sol.y[1]/Delta_t)**(1./3)
            return y[-1]-end_value
        
        def objective_reh_rel(beta0):
            initial_reh = np.array([1.,0,1.-beta0[0]])
            sol_reh = solve_ivp(diff_ext,(ln_den_f,ln_den_end_reh),initial_reh,events=end_evol_ext,t_eval=ln_den_reh,args=(M,beta0[0],omega),method = "DOP853")
            if sol_reh.t[-1]>ln_den_end_reh:
                initial_reh2 = np.array([sol_reh.y[0][-1],1.-beta0[0]*sol_reh.y[0][-1]])
                ln_den_reh2 = np.linspace(sol_reh.t[-1],ln_den_end_reh,10000)
                sol_reh = solve_ivp(diff_ext_rel,(sol_reh.t[-1],ln_den_end_reh),initial_reh2,t_eval=ln_den_reh2,args=(M,beta0[0],omega),method = "DOP853")
            initial = np.array([sol_reh.y[0][-1]])
            ln_den = np.linspace(sol_reh.t[-1],ln_den_end,10000)
            sol = solve_ivp(diff_rad_rel,(sol_reh.t[-1],ln_den_end),initial,t_eval=ln_den,args=(M,beta0[0]),method = "DOP853")
            y = beta0[0]*sol.y[0]*(M_pl_g/M)
            return y[-1]-end_value
    

        # Check if ln_den_f is less than or equal to ln_den_end_reh
        if ln_den_f <= ln_den_end_reh:
            betas_reh_tot.append(betas_full[i])
            continue

        # Create arrays for ln_den_reh and ln_den
        ln_den_reh = np.linspace(ln_den_f,ln_den_end_reh,10000)
        ln_den = np.linspace(ln_den_end_reh,ln_den_end,10000)

        # Solve the differential equation using solve_ivp
        sol1_try = solve_ivp(diff_ext,(ln_den_f,ln_den_end_reh),np.array([1.,0.,1-1e-5]),events=end_evol_ext,t_eval=ln_den_reh,args=(M,1e-5,omega),method = "DOP853")

        # Check if the end of the integration is greater than ln_den_end_reh
        if sol1_try.t[-1] > ln_den_end_reh:
            t = sol1_try.t[-1]
        else:
            sol2_try = solve_ivp(diff_ext,(ln_den_end_reh,ln_den_end),np.array([1e-5*sol1_try.y[0][-1],sol1_try.y[1][-1],0]),events=end_evol_ext,t_eval=ln_den,args=(M,1e-5,0),method = "DOP853")
            t = sol2_try.t[-1]

        # Check if the end of the integration is greater than ln_den_end
        if t > ln_den_end:
            beta_try = Omegas_full[i]*(M/M_pl_g)/(1+(rho_end_reh/rho_end)**(1./4))
            if beta_try>1/2:
                betas_reh_tot.append(1)
                continue
            else:
                beta0, = fsolve(objective_reh_rel,beta_try)
                betas_reh_tot.append(beta0)
        else:
            beta_try = Omegas_full[i]/(1+(rho_end_reh/rho_end)**(1./4))
            beta0, = fsolve(objective_reh,beta_try)
            betas_reh_tot.append(beta0)
            
    return betas_reh_tot






