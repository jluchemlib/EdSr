from typing import Callable, Tuple

from einops import rearrange
import numpy as np

import lammps as lmps
from lammps import IPyLammps, PyLammps, lammps

from tqdm import tqdm



ftm2v_coeff = {
    'lj': 1.0,
    'real': 1.0 / 48.88821291 / 48.88821291,
    'metal': 1.0 / 1.0364269e-4,
    'si': 1.0,
    'cgs': 1.0,
    'electron': 0.937582899,
    'micro': 1.0,
    'nano': 1.0,
}

"""
thermo_style = [
    # energy
    "pe", # total potential energy
    "ke", # kinetic energy
    "etotal", # total energy (pe + ke)
    "evdwl", # van der Waals pairwise energy (includes etail)
    "ecoul", # Coulombic pairwise energy
    "epair", # pairwise energy (evdwl + ecoul + elong)
    "ebond", # bond energy
    "eangle", # angle energy
    "edihed", # dihedral energy
    "eimp", # improper energy
    "emol", # molecular energy (ebond + eangle + edihed + eimp)
    "elong", # long-range kspace energy
    "etail", # van der Waals energy long-range tail correction
    "enthalpy", # enthalpy (etotal + press*vol)
    "ecouple", # cumulative energy change due to thermo/baro statting fixes
    "econserve", # pe + ke + ecouple = etotal + ecouple
    # properties
    "atoms", # number of atoms
    "temp", # temperature
    "press", # pressure
    "vol", # volume
    "density", # mass density of system
    lx,ly,lz = box lengths in x,y,z
]
"""

thermo_style = [
    'custom', 'step', 'time', 'spcpu',
    'temp', 'press',
    'pe', 'ke',
    'enthalpy', 'evdwl', 'ecoul', 'epair',
    'ebond', 'eangle', 'edihed',
    'elong', 'etail', 'emol',
    'ecouple', 'econserve', 'etotal',
    'lx', 'ly', 'lz',
]

def create_simulation(timestep = 0.2, cmdargs = None, num_threads: int = 1, ensemble: str = 'nve') -> IPyLammps:

    lmp = lammps(cmdargs=cmdargs)
    
    MDsimulation = PyLammps(ptr = lmp)

    MDsimulation.enable_cmd_history = True
    if num_threads > 1:
        MDsimulation.package(f"omp {num_threads} neigh yes")
        MDsimulation.suffix('omp')
    
    MDsimulation.units('real')
    MDsimulation.atom_style('full')

    MDsimulation.pair_style('lj/cut/coul/long 12.0')
    MDsimulation.bond_style('harmonic')
    MDsimulation.angle_style('harmonic')
    MDsimulation.dihedral_style('opls')
    MDsimulation.improper_style('cvff')

    MDsimulation.dielectric(1.0)
    MDsimulation.pair_modify('mix arithmetic')
    MDsimulation.special_bonds('lj/coul 0.0 0.0 1.0')
    
    MDsimulation.read_data('../lmps/nvt_1ns_indole.data')

    MDsimulation.atom_modify('sort 0 0.0') # turn off sort algorithm

    MDsimulation.set('type 1 charge -0.55')
    MDsimulation.set('type 2 charge 1.1')

    MDsimulation.group('zeo type 1 2 ')
    MDsimulation.group('indole type 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18')
    
    MDsimulation.kspace_style('pppm', 1e-4)

    MDsimulation.neighbor('5.0 bin')
    MDsimulation.neigh_modify('every 1 delay 0 check yes exclude molecule/intra zeo')

    MDsimulation.delete_bonds('zeo multi')

    MDsimulation.velocity('indole create 700.0 902144 dist gaussian')
    MDsimulation.velocity('zeo set 0.0 0.0 0.0')
    MDsimulation.velocity('indole scale 700.0')

    # if ensemble == 'nvt':
    #     MDsimulation.fix(f'1 indole nvt temp 700.0 700.0 0.01')
    #     # MDsimulation.fix("1 indole temp/rescale 1 700.0 700.0 0.01 1.0")
    #     # MDsimulation.fix("2 indole nve")
    # elif ensemble == 'nve':
    #     MDsimulation.fix('1 indole nve')
    if ensemble == 'nvt':
        MDsimulation.fix('1 indole langevin 700.0 700.0 0.01 902144 tally no')

    MDsimulation.fix('2 indole nve')

    MDsimulation.compute('1 indole temp')

    MDsimulation.thermo_modify('lost/bond ignore')

    MDsimulation.thermo_style(' '.join(thermo_style))

    MDsimulation.timestep(timestep) # attn set timestep

    # initialize system state
    MDsimulation.run(0, 'pre yes post no')

    MDsimulation.enable_cmd_history = False

    return MDsimulation

def create_simulation_beta(timestep = 0.2, cmdargs = None, num_threads: int = 1, ensemble: str = 'nve') -> IPyLammps:

    lmp = lammps(cmdargs=cmdargs)
    
    MDsimulation = PyLammps(ptr = lmp)

    MDsimulation.enable_cmd_history = True
    if num_threads > 1:
        MDsimulation.package(f"omp {num_threads} neigh yes")
        MDsimulation.suffix('omp')
    
    MDsimulation.units('real')
    MDsimulation.atom_style('full')

    MDsimulation.pair_style('lj/cut/coul/long 12.0')
    MDsimulation.bond_style('harmonic')
    MDsimulation.angle_style('harmonic')
    MDsimulation.dihedral_style('opls')
    MDsimulation.improper_style('cvff')

    MDsimulation.dielectric(1.0)
    MDsimulation.pair_modify('mix arithmetic')
    MDsimulation.special_bonds('lj/coul 0.0 0.0 1.0')
    
    MDsimulation.read_data('../lmps/nvt_1ns_indole.data')

    MDsimulation.atom_modify('sort 0 0.0') # turn off sort algorithm

    MDsimulation.set('type 1 charge -0.55')
    MDsimulation.set('type 2 charge 1.1')

    MDsimulation.group('zeo type 1 2 ')
    MDsimulation.group('indole type 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18')
    
    MDsimulation.kspace_style('pppm', 1e-4)

    MDsimulation.neighbor('2.0 bin')
    MDsimulation.neigh_modify('every 1 delay 0 check yes exclude molecule/intra zeo')

    MDsimulation.delete_bonds('zeo multi')

    # MDsimulation.velocity('indole create 700.0 902144 dist gaussian')
    MDsimulation.velocity('zeo set 0.0 0.0 0.0')
    # MDsimulation.velocity('indole scale 700.0')

    # if ensemble == 'nvt':
    #     MDsimulation.fix(f'1 indole nvt temp 700.0 700.0 0.01')
    #     # MDsimulation.fix("1 indole temp/rescale 1 700.0 700.0 0.01 1.0")
    #     # MDsimulation.fix("2 indole nve")
    # elif ensemble == 'nve':
    #     MDsimulation.fix('1 indole nve')
    if ensemble == 'nvt':
        MDsimulation.fix('1 indole langevin 700.0 700.0 0.01 902144 tally no')

    MDsimulation.fix('2 indole nve')

    MDsimulation.compute('1 indole temp')

    MDsimulation.thermo_modify('lost/bond ignore')

    MDsimulation.thermo_style(' '.join(thermo_style))

    MDsimulation.timestep(timestep) # attn set timestep

    # initialize system state
    MDsimulation.run(0, 'pre yes post no')

    MDsimulation.enable_cmd_history = False

    return MDsimulation

def gradientFunction(Lammps: IPyLammps | PyLammps, Position: np.ndarray) -> np.ndarray:
    """
    define the gradient function
    """
    llnp = Lammps.lmp.numpy

    x: np.ndarray = llnp.extract_atom('x')
    x[:] = Position

    before_id = llnp.extract_atom('id').copy()

    Lammps.run(0, 'pre yes post no');

    after_id = llnp.extract_atom('id')

    assert (before_id == after_id).all(), 'array has been changed !!!!!'

    force: np.ndarray = llnp.extract_atom('f')

    return force.copy()



def compute_Taylor(
    Lammps: IPyLammps, 
    SystemState: Tuple[np.ndarray, np.ndarray], 
    Dt: float, 
    maxIter: int, 
    boundary: np.ndarray, 
    shielding_matrix: np.ndarray = None,
    disable_tqdm: bool = False,
) -> Tuple[np.ndarray, np.ndarray, ]:
    """
    core function
    """
    x, v, mass = SystemState

    matrix = np.ones(x.shape)
    
    if shielding_matrix is not None:
        matrix[shielding_matrix] = 0.
        v[shielding_matrix] = 0.

    ftm2v = ftm2v_coeff[Lammps.system.units]
    massinv = matrix * ftm2v / mass

    Dtsq = Dt * Dt

    massinv_Dtsq = massinv * Dtsq

    blo, bhi = boundary
    blen = bhi - blo
    
    xn = x.copy()
    vn = x.copy()
    with tqdm(total = maxIter, desc = 'taylor Iteration: ', leave = False, position = 1, disable = disable_tqdm) as taylor_bar:
        for n in range(maxIter, 0, -1):
            xcoeff = 2.0 * n
            vcoeff = 2.0 * n

            # * compute displacement
            xn_grad = gradientFunction(Lammps, xn)

            # dx = v * Dt + massinv * xn_grad * Dtsq / xcoeff
            # xn = x + dx / (xcoeff - 1)
            xn = x + v * Dt / (xcoeff - 1) + massinv_Dtsq * (1./(xcoeff - 1) - 1./xcoeff) * xn_grad

            # * compute velocity
            vn_grad = gradientFunction(Lammps, vn)

            dv = massinv * vn_grad * Dt / (vcoeff - 1)
            vn = (x + (v + dv) * Dt / (vcoeff - 2)) if n > 1 else (v + dv)

            # attn periodical condition
            # * [blo, bhi) has been desrcibed in LAMMPS
            xn = np.where(xn < blo, xn + blen, xn)
            xn = np.where(xn < bhi, xn, xn - blen)
            if n > 1:
                vn = np.where(vn < blo, vn + blen, vn)
                vn = np.where(vn < bhi, vn, vn - blen)

            taylor_bar.update()
    
    return xn, vn

def compute_Taylor_notqdm(
    Lammps: IPyLammps, 
    SystemState: Tuple[np.ndarray, np.ndarray], 
    Dt: float, 
    maxIter: int, 
    boundary: np.ndarray, 
    shielding_matrix: np.ndarray = None,
    disable_tqdm: bool = False,
) -> Tuple[np.ndarray, np.ndarray, ]:
    """
    core function
    """
    x, v, mass = SystemState

    srcx = Lammps.lmp.numpy.extract_atom('x')
    force = Lammps.lmp.numpy.extract_atom('f')

    matrix = np.ones(x.shape)
    
    if shielding_matrix is not None:
        matrix[shielding_matrix] = 0.
        v[shielding_matrix] = 0.

    ftm2v = ftm2v_coeff[Lammps.system.units]
    massinv = matrix * ftm2v / mass

    Dtsq = Dt * Dt

    massinv_Dtsq = massinv * Dtsq

    blo, bhi = boundary
    blen = bhi - blo
    
    xn = x.copy()
    vn = x.copy()

    for n in range(maxIter, 0, -1):
        xcoeff = 2.0 * n
        vcoeff = 2.0 * n

        # * compute displacement
        # xn_grad = gradientFunction(Lammps, xn)
        srcx[:] = xn
        Lammps.run(0, 'pre yes post no')

        # dx = v * Dt + massinv * xn_grad * Dtsq / xcoeff
        # xn = x + dx / (xcoeff - 1)
        xn = x + v * Dt / (xcoeff - 1) + massinv_Dtsq * (1./(xcoeff - 1) - 1./xcoeff) * force

        # * compute velocity
        # vn_grad = gradientFunction(Lammps, vn)
        srcx[:] = vn
        Lammps.run(0, 'pre yes post no')

        dv = massinv * force * Dt / (vcoeff - 1)
        vn = (x + (v + dv) * Dt / (vcoeff - 2)) if n > 1 else (v + dv)

        # attn periodical condition
        # * [blo, bhi) has been desrcibed in LAMMPS
        xn = np.where(xn < blo, xn + blen, xn)
        xn = np.where(xn < bhi, xn, xn - blen)
        if n > 1:
            vn = np.where(vn < blo, vn + blen, vn)
            vn = np.where(vn < bhi, vn, vn - blen)

    return xn, vn



def execute(
    Lammps: PyLammps | IPyLammps, 
    Dt: float, 
    maxIter: int,
    disable_tqdm: bool = False, 
    scale: bool = False
) -> None:
    """
    execute a step of the whole taylor algorithm
    """
    
    # get the initial state of system
    lmpX, lmpV = Lammps.lmp.numpy.extract_atom('x'), Lammps.lmp.numpy.extract_atom('v')
    lmpMass, atomtype = Lammps.lmp.numpy.extract_atom('mass'), Lammps.lmp.numpy.extract_atom('type')
    
    # set the shielding matrix, True means that gradient set to 0., False is the opposite, shielding matrix is 1-D tensor
    # * set gradient of atoms of id < 3
    shielding_matrix = atomtype < 3

    mass = rearrange(lmpMass[atomtype], 'l -> l 1')

    SystemState = (lmpX.copy(), lmpV.copy(), mass)
    boundary = np.array([
        [Lammps.system.xlo, Lammps.system.ylo, Lammps.system.zlo],
        [Lammps.system.xhi, Lammps.system.yhi, Lammps.system.zhi]
    ])
    
    # newX, newV = compute_Taylor(Lammps, SystemState, Dt, maxIter, boundary, shielding_matrix, disable_tqdm = disable_tqdm)
    newX, newV = compute_Taylor_notqdm(Lammps, SystemState, Dt, maxIter, boundary, shielding_matrix, disable_tqdm = disable_tqdm)

    lmpX[:], lmpV[:] = newX, newV
    
    if scale:
        Lammps.velocity('indole scale 700.0')

    return 

def VelocityVerlet(
    Lammps: PyLammps | IPyLammps, 
    basis_timestep: float, 
    ntimestep: int, 
    disable_tqdm: bool = False
) -> None:

    def execute(Lammps: PyLammps | IPyLammps, Dt: float):
        # get the initial state of system
        lmpX, lmpV = Lammps.lmp.numpy.extract_atom('x'), Lammps.lmp.numpy.extract_atom('v')
        lmpMass, atomtype = Lammps.lmp.numpy.extract_atom('mass'), Lammps.lmp.numpy.extract_atom('type')

        # copy variables
        x_0, v_0 = Lammps.lmp.numpy.extract_atom('x').copy(), Lammps.lmp.numpy.extract_atom('v').copy()
        mass = rearrange(lmpMass[atomtype], "l -> l 1")
        
        # keep the atoms of boundary stationary
        matrix = np.ones_like(x_0)
        matrix[atomtype < 3] = 0.
        v_0[atomtype < 3] = 0.

        ftm2v = ftm2v_coeff[Lammps.system.units]
        massinv = matrix * ftm2v / mass
        Dt_half = Dt * 0.5

        # get gradient at t by using Lammps API and compute v(t + Dt/2)
        force = gradientFunction(Lammps, x_0)
        v_ht = v_0 + massinv * force * Dt_half

        # compute r(t + Dt)
        x_t = x_0 + v_ht * Dt

        # get gradient at t + Dt by using Lammps API and compute v(t + Dt)
        force = gradientFunction(Lammps, x_t)
        v_t = v_ht + massinv * force * Dt_half

        # put x_t, v_t into source address
        lmpX[:] = x_t; lmpV[:] = v_t

    with tqdm(total = ntimestep, desc = 'vv Iteration: ', leave = False, position = 1, disable = disable_tqdm) as vv_bar:
        for _ in range(ntimestep):
            execute(Lammps, basis_timestep)
            vv_bar.update()

    return