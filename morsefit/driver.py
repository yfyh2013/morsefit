"""Defines the driver function for the fitter"""

import sys
import argparse

import numpy as np
from scipy import optimize

from .inputread import read_morse_inp, read_configuration
from .residue import gen_rj_func

def main():

    """The main driver function for the fitter

    The cut-off is given as an optional command line argument, with the actual
    files for the configurations given as positional arguments. The cut-off
    defaults to no cut-off given, and the initial guesses for the Morse
    potential parameters defaults to be in the file ``morse.inp``.

    """

    # parse the arguments
    # -------------------

    parser = argparse.ArgumentParser(description='Fit the Morse potential')
    parser.add_argument('-c', '--cutoff', default=None, action='store',
                        help='The distance cut-off, defalt to no cut-off')
    parser.add_argument('-g', '--guess', default='morse.inp', action='store',
                        help='The file for the Morse parameter guesses')
    parser.add_argument('confs', nargs='+',
                        help='The configuration files')
    args = parser.parse_args()

    try:
        cut_off = float(args.cutoff) if args.cutoff != None else None
    except ValueError:
        print "Invalid cut-off %s given!" % args.cutoff
        sys.exit(1)

    try:
        morse_file = open(args.guess)
    except IOError:
        print "The file %s cannot be opened for the initial guess!" % args.guess
        sys.exit(1)

    # Parse the input files
    # ---------------------

    morse_guess = read_morse_inp(morse_file)
    confs = [ read_configuration(i, cut_off) for i in args.confs ]

    print "Configurations and the initial guess has been read..."

    # Generate the closures
    # ---------------------

    residue, jacobi = gen_rj_func(confs, morse_guess)
    print "Closures for the residue and Jacobian generated..."

    # Perform the fit
    # ---------------

    # Generate the initial guess vector
    ig = np.empty(3 * len(morse_guess))
    for i in xrange(0, len(morse_guess)):
        for j in xrange(0, 3):
            ig[i * 3 + j] = morse_guess[i][1][j]
            continue
        continue
    # The main loop
    print "Entering optimization main loop...\n"
    fit_result = optimize.leastsq(residue, ig, Dfun=jacobi, full_output=True,
                                    col_deriv=True)
    print "\nOptimization finished..."

    # Post processing
    # ---------------

    # Extract the relavant fields from the results.
    res_param = fit_result[0]
    info_dict = fit_result[2]
    mesg = fit_result[3]
    ier = fit_result[4]

    # Convergence testing
    print " Number of function calls: %d" % info_dict['nfev']
    if ier in [1, 2, 3, 4]:
        print "Convergence achieved!"
    else:
        print "Warning: Congences failed for the specified criteria!"
        print " Reason: %s" % mesg

    # Output the comparison of the fitted and Ab-initio energies.
    ab_initio_e = [ i.ab_initio_e for i in confs ]
    file_names = [ i.file_name for i in confs ]
    tags = [ i.tag for i in confs ]
    morse_e = np.array(ab_initio_e) + residue(res_param) 
    print " %20s %20s %25s %25s " %(
            "File Name", "tag", "Ab-initio", "Morse"
            )
    for i in xrange(0, 80):
        sys.stdout.write('*')
        continue
    sys.stdout.write('\n')

    for i in zip(
            file_names, tags, ab_initio_e, morse_e
            ):
        print " %20s %20s %25.10f %25.10f " % i
        continue
    print "\n\n"

    # Write the fitted parameters
    for i in xrange(0, 80):
        sys.stdout.write("*")
        continue
    sys.stdout.write('\n')
    for i, v in enumerate(morse_guess):
        print " %5s %5s  %25.10f %25.10f %25.10f " % (
                v[0][0], v[0][1],
                res_param[i * 3], res_param[i * 3 + 1], res_param[i * 3 + 2]
                )
        continue
    print "\n"

    return 0

