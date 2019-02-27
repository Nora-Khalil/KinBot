"""
Template to run ase search for a ts using Gaussian
KinBot needs to pass to the template: 
1. A label for the calculation
2. The number of cores
3. The kwargs for Gaussian
4. The atom vector
5. The geometry
6. The constraints for the optimization
    a. Fix: The coordinates to fix at their current value
    b. Change: The coordinates to change and fix at the new value
    c. Release: The coordinates to release (only for gaussian)
6. The Gaussian command
"""

import os, sys, re

from math import pi
import numpy as np

import ase
from ase import Atoms
from ase.calculators.gaussian import Gaussian
from ase.optimize import BFGS
from ase.db import connect
from ase.constraints import FixInternals


label = '{label}'
kwargs = {kwargs}

Gaussian.command = '{qc_command} < PREFIX.com > PREFIX.log'
calc = Gaussian(**kwargs)

atom = {atom}
geom = {geom}

mol = Atoms(symbols = atom, positions = geom)
mol.set_calculator(calc)

try:
    e = mol.get_potential_energy() # use the Gaussian optimizer (task optimize)
    """
    #read the geometry from the output file
    outfile = '{label}.log'
    with open(outfile) as f:
        lines = f.readlines()
    for index, line in enumerate(reversed(lines)):
        if re.search('Input orientation:', line) != None:
            for n in range(len(mol)):
                geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
            break
    mol.positions = geom
    """
    db = connect('kinbot.db')
    db.write(mol, name = label, data = {{'energy': e,'status' : 'normal'}})
except RuntimeError: 
    # in case of fail, try again with final geometry
    try:
        #read the geometry from the output file
        outfile = '{label}.log'
        with open(outfile) as f:
            lines = f.readlines()
        for index, line in enumerate(reversed(lines)):
            if re.search('Input orientation:', line) != None:
                for n in range(len(mol)):
                    geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                break
        mol.positions = geom
        e = mol.get_potential_energy() # use the Gaussian optimizer
        #read the geometry from the output file
        outfile = '{label}.log'
        with open(outfile) as f:
            lines = f.readlines()
        for index, line in enumerate(reversed(lines)):
            if re.search('Input orientation:', line) != None:
                for n in range(len(mol)):
                    geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                break
        mol.positions = geom
        db = connect('kinbot.db')
        db.write(mol, name = label, data = {{'energy': e,'status' : 'normal'}})
    except:
        try:
            #read the geometry from the output file
            outfile = '{label}.log'
            with open(outfile) as f:
                lines = f.readlines()
            for index, line in enumerate(reversed(lines)):
                if re.search('Input orientation:', line) != None:
                    for n in range(len(mol)):
                        geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                    break
            mol.positions = geom
            e = mol.get_potential_energy() # use the Gaussian optimizer
            #read the geometry from the output file
            outfile = '{label}.log'
            with open(outfile) as f:
                lines = f.readlines()
            for index, line in enumerate(reversed(lines)):
                if re.search('Input orientation:', line) != None:
                    for n in range(len(mol)):
                        geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                    break
            mol.positions = geom
            db = connect('kinbot.db')
            db.write(mol, name = label, data = {{'energy': e,'status' : 'normal'}})
        except:
            try:
                #read the geometry from the output file
                outfile = '{label}.log'
                with open(outfile) as f:
                    lines = f.readlines()
                for index, line in enumerate(reversed(lines)):
                    if re.search('Input orientation:', line) != None:
                        for n in range(len(mol)):
                            geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                        break
                mol.positions = geom
                del kwargs['opt']  # this is when we give up optimization!!
                e = mol.get_potential_energy() # use the Gaussian optimizer
                #read the geometry from the output file
                outfile = '{label}.log'
                with open(outfile) as f:
                    lines = f.readlines()
                for index, line in enumerate(reversed(lines)):
                    if re.search('Input orientation:', line) != None:
                        for n in range(len(mol)):
                            geom[n][0:3] = np.array(lines[-index+4+n].split()[3:6]).astype(float)
                        break
                mol.positions = geom
                db = connect('kinbot.db')
                db.write(mol, name = label, data = {{'energy': e,'status' : 'normal'}})
            except: 
                db = connect('kinbot.db')
                db.write(mol, name = label, data = {{'status' : 'error'}})


f = open(label + '.log', 'a')
f.write('done\n')
f.close()


