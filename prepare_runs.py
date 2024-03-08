#!/bin/env python

import sys, os

gro = "../alaTB_ff03_tip3p_npt.gro"
top = "../alaTB_ff03_tip3p.top"
toppp = "../alaTB_ff03_tip3p_pp.top"
mdp = "../sd_nvt.mdp"
tpr = "alaTB_ff03_tip3p_nvt.tpr"

gmx = "/home/david/anaconda3/envs/plumed-mpi/bin/gmx_mpi" 
#gmx = "/Users/daviddesancho/opt/anaconda3/envs/plumed-mpi/bin/gmx_mpi"
#command = gmx + " grompp -f %s -p %s -c %s -o %s -pp %s"%(mdp, top, gro, tpr, toppp)
#os.system(command)
#
#command = "mpirun -np 1 gmx_mpi mdrun -s %s  -ntomp 1 -nsteps 10000"%tpr
#os.system(command)

# scale solute interactions
tmax = 600
t0 = 300
for nrep in [2, 4, 8, 16]:
    try:
        os.mkdir("nrep%i"%nrep)
    except OSError as e:
            print (e)

    for i in range(nrep):
        #        exponent = i/(nrep - 1)
        exponent = i/(16 - 1)
        ti = t0*(tmax/t0)**exponent 
        lmbd = t0/ti
        print ("Run %i; lambda=%.2f"%(i,lmbd))

        folder = "nrep%i/rep%i"%(nrep,i)
        try:
            os.mkdir(folder)
        except OSError as e:
            print (e)
        
        command = "plumed partial_tempering %g < %s > %s/scaled.top"%(lmbd, toppp, folder)
        os.system(command)

        top = "%s/scaled.top"%folder 
        tpr = "%s/alaTB_ff03_tip3p_nvt.tpr"%folder
        command = gmx + " grompp -f %s -p %s -c %s -o %s"%(mdp, top, gro, tpr)
        os.system(command)
    
    dirs = ["nrep%i/rep%i "%(nrep, j) for j in range(nrep)]
    dirs = ''.join(dirs)
    print (dirs)

    tpr = "alaTB_ff03_tip3p_nvt.tpr"
    command = "mpiexec --mca opal_cuda_support 1 -np %i %s mdrun -s %s -multidir %s -nsteps 250000 -plumed ../../plumed.dat -hrex -replex 100 -ntomp 1"%(nrep, gmx, tpr, dirs)
    os.system(command)
