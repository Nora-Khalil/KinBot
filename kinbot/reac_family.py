###################################################
##                                               ##
## This file is part of the KinBot code v2.0     ##
##                                               ##
## The contents are covered by the terms of the  ##
## BSD 3-clause license included in the LICENSE  ##
## file, found at the root.                      ##
##                                               ##
## Copyright 2018 National Technology &          ##
## Engineering Solutions of Sandia, LLC (NTESS). ##
## Under the terms of Contract DE-NA0003525 with ##
## NTESS, the U.S. Government retains certain    ##
## rights to this software.                      ##
##                                               ##
## Authors:                                      ##
##   Judit Zador                                 ##
##   Ruben Van de Vijver                         ##
##                                               ##
###################################################
"""
Generic methods for the reaction families
"""

from __future__ import print_function
import os
import numpy as np
import copy
import time
import pkg_resources
from kinbot import modify_geom

def carry_out_reaction(rxn, step, command):
    """
    Verify what has been done and what needs to be done
    
    skip: boolean which tells to skip the first 12 steps in case of an instance shorter than 4
    
    scan: boolean which tells if this is part of an energy scan along a bond length coordinate
    """
    if step > 0:
        status = rxn.qc.check_qc(rxn.instance_name)
        if status != 'normal' and status != 'error': return step

    kwargs = rxn.qc.get_qc_arguments(   rxn.instance_name, rxn.species.mult, rxn.species.charge, ts = 1,
                                        step = step, max_step=rxn.max_step, scan = rxn.scan)

    if step == 0:
        if rxn.qc.is_in_database(rxn.instance_name):
            if rxn.qc.check_qc(rxn.instance_name) == 'normal': 
                err, freq = rxn.qc.get_qc_freq(rxn.instance_name, rxn.species.natom)
                if err == 0 and len(freq) > 0.:
                    err, geom = rxn.qc.get_qc_geom(rxn.instance_name, rxn.species.natom)
                    step = rxn.max_step + 1
                    return step
        if rxn.skip and len(rxn.instance) < 4: 
            step = 12
        geom = rxn.species.geom
    else:
        err, geom = rxn.qc.get_qc_geom(rxn.instance_name, rxn.species.natom, allow_error = 1)
    
    step, fix, change, release = rxn.get_constraints(step, geom)

    if step > rxn.max_step:
        return step
    
    pcobfgs = 0
    if pcobfgs == 0:
        #apply the geometry changes here and fix the coordinates that changed
        change_starting_zero = []
        for c in change:
            c_new = [ci - 1 for ci in c[:-1]]
            c_new.append(c[-1])
            change_starting_zero.append(c_new)

        geom2 = ''
        for i, at in enumerate(rxn.species.atom):
            if i > 0:
                geom2 += '            '
                x, y, z = rxn.species.geom[i]
                geom2 += '{} {:.6f} {:.6f} {:.6f}\n'.format(rxn.species.atom[i], x, y, z)
 
        a=str(len(rxn.species.atom)-1)
        g=open('bfgs_geom.log','a')
        g.write(a)
        g.write("\nOriginal Geom, chemid: {}\n".format(rxn.species.chemid))
        g.write(geom2)
        g.close()

        if len(change_starting_zero) >0 :
            success, geom = modify_geom.modify_coordinates(rxn.species, rxn.instance_name, geom, change_starting_zero, rxn.species.bond)
            for c in change:
                fix.append(c[:-1])
            change = []

        geom3 = ''
        for i, at in enumerate(rxn.species.atom):
            if i > 0:
                geom3 += '            '
                x, y, z = rxn.species.geom[i]
                geom3 += '{} {:.6f} {:.6f} {:.6f}\n'.format(rxn.species.atom[i],x, y, z)

        g=open('bfgs_geom.log','a')
        g.write(a)
        g.write("\nNew Geom, chemid: {}\n".format(rxn.species.chemid))
        g.write(geom3)
        g.close()

        kwargs['fix'] = fix
        kwargs['change'] = change
        kwargs['release'] = release

        if step < rxn.max_step:
            template_file = pkg_resources.resource_filename('tpl', 'ase_{qc}_ts_search.py.tpl'.format(qc=rxn.qc.qc))
            template = open(template_file,'r').read()
        else:
            template_file = pkg_resources.resource_filename('tpl', 'ase_{qc}_ts_end.py.tpl'.format(qc=rxn.qc.qc))
            template = open(template_file,'r').read()
        
        template = template.format(label=rxn.instance_name, 
                                   kwargs=kwargs, 
                                   atom=list(rxn.species.atom), 
                                   geom=list([list(gi) for gi in geom]), 
                                   ppn=rxn.qc.ppn,
                                   qc_command=command,
                                   working_dir=os.getcwd())
    else:
        # use the pcobfgs algorithm for the geometry update
        if step < rxn.max_step:
            del kwargs['opt']
            conv_crit = 0.01  # force convergence criterion 
            template_file = pkg_resources.resource_filename('tpl', 'ase_{qc}_ts_search_pcobfgs.py.tpl'.format(qc = rxn.qc.qc))
            template = open(template_file,'r').read()
            template = template.format(label=rxn.instance_name, kwargs=kwargs, atom=list(rxn.species.atom), 
                                       geom=list([list(gi) for gi in geom]), ppn=rxn.qc.ppn, fix=fix,
                                       change=change, conv_crit=conv_crit)
        else:
            template_file = pkg_resources.resource_filename('tpl', 'ase_{qc}_ts_end.py.tpl'.format(qc = rxn.qc.qc))
            template = open(template_file,'r').read()
            template = template.format(label = rxn.instance_name, kwargs = kwargs, atom = list(rxn.species.atom), 
                                       geom = list([list(gi) for gi in geom]), ppn = rxn.qc.ppn, qc_command=command)
    
    f_out = open('{}.py'.format(rxn.instance_name),'w')
    f_out.write(template)
    f_out.close()
    
    step += rxn.qc.submit_qc(rxn.instance_name, 0)

    return step
    
