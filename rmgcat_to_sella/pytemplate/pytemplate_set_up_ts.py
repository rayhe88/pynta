#!/usr/bin/env python3
import os
import datetime

from rmgcat_to_sella.balsamcalc import EspressoBalsamSocketIO

from ase.io import read, write
from ase.constraints import FixAtoms
from sella import Sella

rxn_name = '{rxn_name}'
prefix = '{prefix}'
geom = '{ts_fname}'
balsam_exe_settings = {balsam_exe_settings}
calc_keywords = {calc_keywords}

trajdir = os.path.join(prefix, prefix + '_' + rxn_name + '.traj')
label = os.path.join(prefix, prefix)

start = datetime.datetime.now()
with open(label + '_time.log', 'w+') as f:
    f.write(str(start))
    f.write("\n")
    f.close()

ts_atom = read(os.path.join(prefix, geom))
# fix all atoms but not adsorbates
# ts_atom.set_constraint(FixAtoms([
#     atom.index for atom in ts_atom if atom.index < len(ts_atom) - 2
# ]))
# fix bottom half of the slab
ts_atom.set_constraint(FixAtoms([
    atom.index for atom in ts_atom if atom.position[2] < ts_atom.cell[2, 2] / 2.
]))

extra_calc_keywords = dict(
    pseudopotentials={pseudopotentials},
    pseudo_dir='{pseudo_dir}',
    label=prefix
)

ts_atom.calc = EspressoBalsamSocketIO(
    workflow='QE_Socket',
    job_kwargs=balsam_exe_settings,
    **calc_keywords
)

ts_atom.calc.set(**extra_calc_keywords)

opt = Sella(ts_atom, order=1, delta0=1e-2, gamma=1e-3, trajectory=trajdir)
opt.run(fmax=0.01)
ts_atom.calc.close()

write_dir = os.path.join(prefix, prefix + '_' + rxn_name)
write(write_dir + '_ts_final.png', read(trajdir))
write(write_dir + '_ts_final.xyz', read(trajdir))

end = datetime.datetime.now()
with open(label + '_time.log', 'a+') as f:
    f.write(str(end))
    f.write("\n")
    f.write(str(end - start))
    f.write("\n")
    f.close()
