#!/usr/bin/env python3

import os

import datetime
from rmgcat_to_sella.balsamcalc import EspressoBalsamSocketIO

from ase.constraints import FixAtoms
from ase.vibrations import Vibrations
from ase.io import read

geom = '{geom}'
prefix = geom[:2]
balsam_exe_settings = {balsam_exe_settings}
calc_keywords = {calc_keywords}
creation_dir = '{creation_dir}'
nimages = {nimages}
n = {n}
vib_files_loc = os.path.join(os.getcwd(), prefix, 'vib')
geom_prefix = os.path.join(prefix, geom[:-10])

start = datetime.datetime.now()

with open(geom_prefix + '_time.log', 'w+') as f:
    f.write(str(start))
    f.write("\n")
    f.close()

atoms = read(os.path.join(prefix, geom))

# freeze all surface atoms
atoms.set_constraint(FixAtoms(
    [atom.index for atom in atoms if atom.symbol == 'Cu']))
# vibrate only adsorbed species
indices = [atom.index for atom in atoms if atom.symbol != 'Cu']

extra_calc_keywords = dict(
    pseudopotentials={pseudopotentials},
    pseudo_dir='{pseudo_dir}',
    label=geom
)

atoms.calc = EspressoBalsamSocketIO(
    workflow='QE_Socket',
    job_kwargs=balsam_exe_settings,
    **calc_keywords
)

atoms.calc.set(**extra_calc_keywords)

# start vibrations calculations
vib = Vibrations(atoms, indices=indices, name=vib_files_loc)
vib.run()
vib.summary()
# vib.clean()

# write the first vibration mode to vib.0.traj file (default) - imaginary freq
vib.write_mode(n=n, nimages=nimages)

end = datetime.datetime.now()

with open(os.path.join(prefix, geom[:-10] + '_time.log'), 'a+') as f:
    f.write(str(end))
    f.write("\n")
    f.write(str(end - start))
    f.write("\n")
    f.close()
