from __future__ import print_function

import numpy as np

# Import sile objects
from .sile import SileVASP
from ..sile import *

# Import the geometry object
from sisl.messages import warn
from sisl import Geometry, PeriodicTable, Atom, SuperCell

__all__ = ['carSileVASP']


class carSileVASP(SileVASP):
    """ Geometry informaation

    This file-object handles both POSCAR and CONTCAR files
    """

    def _setup(self, *args, **kwargs):
        """ Setup the `poscarSile` after initialization """
        self._scale = 1.

    @sile_fh_open()
    def write_geometry(self, geom):
        """ Writes the geometry to the contained file """
        # Check that we can write to the file
        sile_raise_write(self)

        # LABEL
        self._write('sisl output\n')

        # Scale
        self._write('  1.\n')

        # Write unit-cell
        fmt = ('   ' + '{:18.9f}' * 3) + '\n'
        tmp = np.zeros([3], np.float64)
        for i in range(3):
            tmp[:3] = geom.cell[i, :]
            self._write(fmt.format(*tmp))

        # Figure out how many species
        pt = PeriodicTable()
        s, d = [], []
        for ia, a, idx_specie in geom.iter_species():
            if idx_specie >= len(d):
                s.append(pt.Z_label(a.Z))
                d.append(0)
            d[idx_specie] += + 1
        fmt = ' {:s}' * len(d) + '\n'
        self._write(fmt.format(*s))
        fmt = ' {:d}' * len(d) + '\n'
        self._write(fmt.format(*d))
        self._write('Cartesian\n')

        fmt = '{:18.9f}' * 3 + '\n'
        for ia in geom:
            self._write(fmt.format(*geom.xyz[ia, :]))

    @sile_fh_open(True)
    def read_supercell(self):
        """ Returns `SuperCell` object from the CONTCAR/POSCAR file """

        # read first line
        self.readline()  # LABEL
        # Update scale-factor
        self._scale = float(self.readline())

        # Read cell vectors
        cell = np.empty([3, 3], np.float64)
        for i in range(3):
            cell[i, :] = list(map(float, self.readline().split()[:3]))
        cell *= self._scale

        return SuperCell(cell)

    @sile_fh_open()
    def read_geometry(self):
        """ Returns Geometry object from the CONTCAR/POSCAR file
        """
        sc = self.read_supercell()

        # The species labels are not always included in *CAR
        line1 = self.readline().split()
        opt = self.readline()
        try:
            species = line1
            species_count = np.array(opt.split(), np.int32)
        except:
            species_count = np.array(line1, np.int32)
            # We have no species...
            # We default to consecutive elements in the
            # periodic table.
            species = [i+1 for i in range(len(species_count))]
            err = '\n'.join([
                "POSCAR best format:",
                "  <Specie-1> <Specie-2>",
                "  <#Specie-1> <#Specie-2>",
                "Format not found, the species are defaulted to the first elements of the periodic table."])
            warn(err)

        # Create list of atoms to be used subsequently
        atom = [Atom[spec]
                for spec, nsp in zip(species, species_count)
                for i in range(nsp)]

        # Read whether this is selective or direct
        # Currently direct is not used
        opt = self.readline()
        #direct = True
        if opt[0] in 'Ss':
            #direct = False
            opt = self.readline()

        # Check whether this is in fractional or direct
        # coordinates
        cart = False
        if opt[0] in 'CcKk':
            cart = True

        # Number of atoms
        na = len(atom)

        xyz = np.empty([na, 3], np.float64)
        for ia in range(na):
            xyz[ia, :] = list(map(float, self.readline().split()))
        if cart:
            # The unit of the coordinates are cartesian
            xyz *= self._scale
        else:
            xyz = np.dot(xyz, sc.cell.T)

        # The POT/CONT-CAR does not contain information on the atomic species
        return Geometry(xyz=xyz, atom=atom, sc=sc)

    def ArgumentParser(self, p=None, *args, **kwargs):
        """ Returns the arguments that is available for this Sile """
        newkw = Geometry._ArgumentParser_args_single()
        newkw.update(kwargs)
        return self.read_geometry().ArgumentParser(p, *args, **newkw)


add_sile('CAR', carSileVASP, gzip=True)
add_sile('POSCAR', carSileVASP, gzip=True)
add_sile('CONTCAR', carSileVASP, gzip=True)
