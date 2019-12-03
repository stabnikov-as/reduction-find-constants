#!/bin/env python
import os
import time
import subprocess
import shlex
import sys
import numpy as np
import pylab as plt
from scipy import interpolate
from datetime import datetime as dt

#------------------------------------------------------#
def get_datetime():
    '''
    gets date and time in a str in format
    yyyy-mm-dd_hh:mm:ss
    :return: string with date and time
    '''
    return str(dt.now())[:-7].replace(' ', '_')

#----------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------Constant-Values---------------------------------------------------------#
Cts  = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
Ats  = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
Csss = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
a2s  = [0.4, 0.5, 0.6, 0.7]

#----------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------Filenames-and-other-constants-------------------------------------------#
#----------------------------------------------------------------and-magic-numbers-------------------------------------------------#
di_fname = 'di_uduct.tec'
exp_fname = 't3a_exp.tec'
log_fn  = 'log' + get_datetime() + '.txt' # Name of log output file


#------------------------------------------------------#
def read_file(fn):
    '''
    Reads file
    :param fn: str, filename
    :return: list, a list of strings of a file
    '''
    with open(fn, 'r') as f:
        content = f.readlines()
    return content

def run_cmd(cmd, cwd = None):
    '''
    Function for running Linux command
    :param cmd: str, containing the command
    :param cwd: str, containing cwd attribute the path to directory from where to run the command
    :return: tuple of 2 str, command output and error code
    '''
    command = shlex.split(cmd)
    p = subprocess.Popen(command,
	stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd = cwd)
    out, err = p.communicate()
    return (out, err)

def write_log_header():
    '''
    Creates log file and writes it's header
    :return:
    '''
    with open(log_fn, "w") as f:
        f.write('{} -- Log start\n'.format(get_datetime()))

def add_to_log(string):
    '''
    Adds a string to log file with datetime stamp
    :param string: str, a string to add to log
    :return: no return
    '''
    with open(log_fn, "a") as f:
        f.write('{} -- {}\n'.format(get_datetime(), string))

def parse_di_file(lines):
    Rex = []
    cf = []
    for i in range(3, len(lines)):
        Rex.append((float(lines[i].split()[0])-0.07)*1e6)
        cf.append(float(lines[i].split()[2]))
    return np.array(Rex), np.array(cf)

def parse_exp_data(lines):
    Rex = []
    cf = []
    for i in range(1, len(lines)):
        Rex.append(float(lines[i].split(',')[0]))
        cf.append(float(lines[i].split(',')[1]))
    return np.array(Rex), np.array(cf)



def main():
    Rex_exp, cf_exp = parse_exp_data(read_file(exp_fname))

    #plt.clf()
    #plt.plot(Rex_di, cf_di, 'r--', label='di')
    #plt.plot(Rex_exp, cf_exp, 'b-', label='exp')


    # plt.plot(Rex_exp, f(Rex_exp), 'g', label='interpolated')
    # plt.axis([0.0, 5e5, 0.0, 0.01])
    # plt.show()
    # print(error)

    write_log_header()  # Initialize log file
    add_to_log('Cts = ' + str(Cts))  # Add info on constants to log file
    add_to_log('Ats = ' + str(Ats))
    add_to_log('Csss = ' + str(Csss))
    add_to_log('a2s = ' + str(a2s))
    a2 = a2s[0]
    i = 0  # Variable to count tasks started
    cmd_path = 'pwd'  # Command to get current pwd
    (o, e) = run_cmd(cmd_path)
    pwd = o.split('\n')[0] + '/'
    total_tasks = len(Ats) * len(Cts) * len(Csss) * len(a2s)
    add_to_log('amount of jobs = {}'.format(total_tasks))
    add_to_log('max jobs       = {}'.format(max_jobs))
    min_error = 0
    for ct in Cts:  # Nested loops over all constants
        path1 = 'Ct_=_' + str(ct)
        add_to_log('\n')
        add_to_log('----------------------------------{}% complete\n'.format(float(i) / float(total_tasks) * 100.0))
        add_to_log(' ')
        add_to_log(path1)
        for at in Ats:
            path2 = '/At_=_' + str(at)
            add_to_log('  ' + path2[1:])
            for css in Csss:
                path3 = '/Css_=_' + str(css)
                path = path1 + path2 + path3
                add_to_log('    ' + path3[1:])
                for a2 in a2s:
                    i += 1
                    path4 = '/a2_=_' + str(a2)
                    path = path1 + path2 + path3 + path4
                    di_path = path + '/' + di_fname
                    Rex_di, cf_di = parse_di_file(read_file(di_path))
                    f = interpolate.interp1d(Rex_di, cf_di)
                    di_exp_points = f(Rex_exp)
                    error = np.sum((di_exp_points - cf_exp)**2.0)**0.5/len(Rex_exp)
                    if error < min_error:
                        min_error = error
                        add_to_log('New min error found {} for {}'.format(min_error, path))




    add_to_log(' ')
    add_to_log('Program finished')


if __name__ == '__main__':
    main()
