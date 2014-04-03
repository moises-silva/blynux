#!/usr/bin/env python
# vim: tabstop=4 softtabstop=4 shiftwidth=4 textwidth=80 smarttab expandtab
from __future__ import with_statement
import psutil
import os
import sys
import subprocess
import time
from distutils import spawn

VIM_EXTENSIONS = ( 'c', 'cpp', 'sh', 'cs', 'py', 'pl', 'rb', 'js' )

def set_color(c):
    blynux_bin = 'blynux'
    cmd = [blynux_bin, '--device', '0', '--color', c]
    subprocess.call(cmd)

def screensaver_active():
    try:
        ssbin = spawn.find_executable('gnome-screensaver-command')
        if ssbin is None:
            return False
        cmd = [ssbin, '-q']
        o = subprocess.check_output(cmd)
        if 'inactive' in o:
            return False
        return True
    except:
        return False

def is_vim_coding(proc):
    if proc.name != 'vim':
        return False
    fname = proc.cmdline[1]
    i = fname.rfind('.')
    if i < 0:
        try:
            ffname = proc.getcwd() + os.sep + fname
            with open(ffname, 'r') as f:
                if f.read(2) == '#!':
                    return True
        except:
            pass
    elif fname[i+1:] in VIM_EXTENSIONS:
        return True
    return False

timeout = 10
timer = 0
busy = False
sleep_interval = 1
set_color('green')
try:
    while True:
        if screensaver_active():
            set_color('OFF')
            busy = False
            time.sleep(sleep_interval)
            continue
        vim_found = False
        for proc in psutil.process_iter():
            if is_vim_coding(proc):
                vim_found = True
                break

        if vim_found:
            if not busy:
                set_color('red')
                busy = True
                timer = timeout

        elif busy and timer > 0:
            timer = timer - 1
            if timer == 0:
                busy = False
                set_color('green')

        time.sleep(sleep_interval)
except KeyboardInterrupt:
    pass

