# Quickstar

## Importing Modules

```{note}
One way to verify that the betaPBH library has been installed correctly is to immediately import the library and all its modules.
```

1. Import the PBHBeta library and any required modules:

```{code-block}
from PBHBeta import *
import matplotlib.pyplot as plt
import numpy as np
```


2. Generate an array of masses using the put_M_array function:

The first function to execute is {py:func}`PBHBeta.functions.put_M_array`, which contains the instruction to generate an array of masses from a maximum value of mass in grams.

```{code-block}
PBHBeta.functions.put_M_array(1e20)
```
```{note}
The library contains a module called `constraints.py`, where the `return` of {py:func}`PBHBeta.functions.put_M_array` will be stored.
```

3. Access the generated masses stored in the `constraints.M_tot` variable:

You can retrieve the values stored in `constraint.M_tot` and store them in a variable to perform operations within the PBHBeta functions. 

Here's an example:

```{code-block} python
:lineno-start: 1
M_tot = constraints.M_tot
```

4. Calculate the abundances (betas) considering the dark matter (DM) constraints using the Betas_DM function {py:func}`PBHBeta.functions.Betas_DM()` with input `M_tot`:

```{code-block} python
:lineno-start: 2
functions.Betas_DM(M_tot)
```

```{note}
The documentation of the `PBHBeta.functions.Betas_DM()` function specifies that it stores the values of the total abundance in an array called `betas_DM_tot` within the `constraints.py` module. Additionally, the function returns four arrays, namely `M_n`, `betas`, `M_relic`, and `betas_relic`.

To manipulate these arrays, you can directly access them by invoking `functions.Betas_DM(M_tot)`[number], where `number` can be 0, 1, 2, or 3, corresponding to each output array respectively.

```

5. Plot the calculated abundances using matplotlib:

```{code-block} python
:lineno-start: 3
plt.loglog(functions.Betas_DM(M_tot)[0],functions.Betas_DM(M_tot)[1], "k:",label=r"$\Omega_{DM}$")
plt.fill_between(functions.Betas_DM(M_tot)[0],functions.Betas_DM(M_tot)[1], functions.Betas_DM(M_tot)[1]*0+10, color='grey',alpha=0.2)
plt.loglog(functions.Betas_DM(M_tot)[2],functions.Betas_DM(M_tot)[3], "k:",label=r"$\Omega_{DM}$")
plt.fill_between(functions.Betas_DM(M_tot)[2],functions.Betas_DM(M_tot)[3], functions.Betas_DM(M_tot)[3]*0+10, color='grey',alpha=0.2)
plt.xlabel(r"$M_{\rm PBH}~[\rm{g}]$")
plt.ylabel(r"$\beta$")
plt.xlim([1,1e20])
plt.ylim([1e-30,1])

plt.legend()
plt.show()
```

`out:`
```{figure} img/IMG_DM.png
:alt: fishy
:class: bg-primary
:width: 500px
:align: center
```

Congratulations! You have successfully installed and used `PBHBeta`. You can explore more functionalities and examples in the library's documentation.
