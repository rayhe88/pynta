from rmgcat_to_sella.excatkit.molecule import Molecule
from rmgcat_to_sella.excatkit.gratoms import Gratoms
from typing import List, Dict, Tuple
from collections import Counter


class TSEstimator():
    @staticmethod
    def build_ts_guess(ts_est: str) -> Gratoms:
        ''' Convert ts_est string into a list of Gratoms objects.

            Numner of elements in the list depends is equal to number of
            distinct topologies available for given ts_est.

            For diatomics there will always be one element in the list.
            For other types, more than one structure is possible, e.g.
            ts_est = 'COH' --> ts_guess_list = ['COH' (sp), 'CHO' (sp2)]

        Parameters
        ----------
        ts_est : str
            a string representing species that will be used to get ts_guess
            e.g. 'OH', 'COH'

        Returns
        -------
        ts_guess_list : List[Gratoms]
            a list of Gratoms objects with all distinct topologies for a given
            ts_est

        '''
        ts_guess_list = Molecule().molecule(ts_est)
        return ts_guess_list

    def deal_with_bonds(
            self,
            ts_guess_el,
            rxn,
            reacting_sp):
        surface_bonded_atoms = self.get_surface_bonded_atoms(
            rxn, reacting_sp)
        if len(surface_bonded_atoms) > 1:
            raise NotImplementedError(
                'Only one atom can be connectedto the surface. '
                'Support for many atoms will be added later.')
        else:
            bonded = surface_bonded_atoms[0]
            surface_bonded_atom_idx = self.get_bonded_index(
                bonded, ts_guess_el)
        return surface_bonded_atom_idx

    @staticmethod
    def get_surface_bonded_atoms(
            rxn,
            reacting_sp):
        atomic_connections = TSEstimator.get_atomic_connections(
            rxn, reacting_sp)
        surface_bonded_atoms = []
        for k, v in atomic_connections.items():
            if v == max(atomic_connections.values()):
                surface_bonded_atoms.append(k)
        return surface_bonded_atoms

    @staticmethod
    def get_bonded_index(
            bonded,
            ts_guess_el):
        symbol = str(ts_guess_el.symbols)
        surface_bonded_atom_idx = symbol.find(bonded)
        return surface_bonded_atom_idx

    @staticmethod
    def get_atomic_connections(
            rxn,
            reacting_sp):
        atomic_connections = {}
        reacting_sp_connectivity = rxn[reacting_sp].split('\n')
        for line in reacting_sp_connectivity:
            if '*' in line:
                connections = line.count('{')
                symbol = line.split()[2]
                atomic_connections[symbol] = connections
        return atomic_connections

    @staticmethod
    def get_reacting_atoms_indices(
            ts_guess_el,
            reacting_atoms):
        symbol = str(ts_guess_el.symbols)
        reacting_atom_indicies = {}
        for species in reacting_atoms:
            # deal with edge case when there are two the same type (eg. CO2)
            add = 0
            if TSEstimator.is_double_atom(ts_guess_el, species):
                add = 1
            reacting_atom_indicies[species] = symbol.find(species) + add

        if len(reacting_atom_indicies) > 2:
            raise NotImplementedError('Only two atoms can take part in '
                                      'reaction')
        return reacting_atom_indicies

    @staticmethod
    def is_double_atom(
            ts_guess_el,
            species):
        atom_list = [atom.symbol for atom in ts_guess_el]
        count = Counter(atom_list)
        if count[species] > 1:
            return True
        return False


class Diatomic(TSEstimator):
    def get_ts_guess_and_bonded_idx(
            self,
            ts_est: str,
            rxn: Dict[str, str],
            reacting_sp: str,
            reacting_atoms: List[str],
            scfactor: float) -> Tuple[Gratoms, int]:
        ts_guess_list = Diatomic.build_ts_guess(ts_est)
        # For diatimics, there is only one possible topology, so
        ts_guess_el = ts_guess_list[0]
        return self.rotate_and_scale(ts_guess_el, rxn, reacting_sp,
                                     reacting_atoms, scfactor)

    def rotate_and_scale(
            self,
            ts_guess_el,
            rxn,
            reacting_sp,
            reacting_atoms,
            scfactor):
        surface_bonded_atom_idx = self.deal_with_bonds(
            ts_guess_el, rxn, reacting_sp)
        reacting_atom_indicies = Diatomic.get_reacting_atoms_indices(
            ts_guess_el, reacting_atoms)

        react_ind_1, react_ind_2 = reacting_atom_indicies.values()

        bondlen = ts_guess_el.get_distance(react_ind_1, react_ind_2)
        ts_guess_el.rotate(90, 'y')
        ts_guess_el.set_distance(
            react_ind_1, react_ind_2, bondlen * scfactor, fix=0)
        return ts_guess_el, surface_bonded_atom_idx


class Triatomic(TSEstimator):
    def get_ts_guess_and_bonded_idx(
            self,
            ts_est,
            rxn,
            reacting_sp,
            reacting_atoms,
            scfactor,
            conf=None):
        ts_guess_list = Triatomic.build_ts_guess(ts_est)
        if conf == 'sp':
            ts_guess_el = ts_guess_list[1]
        else:
            ts_guess_el = ts_guess_list[0]

        return self.rotate_and_scale(ts_guess_el, rxn, reacting_sp,
                                     reacting_atoms, scfactor)

    def rotate_and_scale(
            self,
            ts_guess_el,
            rxn,
            reacting_sp,
            reacting_atoms,
            scfactor):
        surface_bonded_atom_idx = self.deal_with_bonds(
            ts_guess_el, rxn, reacting_sp)
        reacting_atom_indicies = Triatomic.get_reacting_atoms_indices(
            ts_guess_el, reacting_atoms)

        react_ind_1, react_ind_2 = reacting_atom_indicies.values()

        bondlen = ts_guess_el.get_distance(react_ind_1, react_ind_2)
        ts_guess_el.rotate(90, 'z')
        ts_guess_el.set_distance(
            react_ind_1, react_ind_2, bondlen * scfactor, fix=0)
        # hardcoded values based on empirical tests
        ts_guess_el.set_angle(
            0, 1, 2, -30, indices=[0, 1, 2], add=True)
        return ts_guess_el, surface_bonded_atom_idx
