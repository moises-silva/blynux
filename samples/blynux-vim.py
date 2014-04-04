#!/usr/bin/env python
# vim: tabstop=4 softtabstop=4 shiftwidth=4 textwidth=80 smarttab expandtab
from __future__ import with_statement
import psutil
import os
import sys
import subprocess
import time
import os
import logging
from distutils import spawn
from logging.handlers import SysLogHandler

VIM_EXTENSIONS = ( 'c', 'cpp', 'sh', 'cs', 'py', 'pl', 'rb', 'js' )

timeout = 10
timer = 0
busy = False
sleep_interval = 1
ssaver = False
last_color = ''

logger = logging.getLogger(os.path.basename(sys.argv[0]))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
syslog_handler = SysLogHandler('/dev/log')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)
if sys.stdout.isatty():
    try:
        import colorlog
        colors = {
            'CRITICAL': 'bold_red',
            'DEBUG': 'yellow',
            'ERROR': 'bold_red',
            'INFO': 'green',
            'WARNING': 'red',
        }
        formatter = colorlog.ColoredFormatter('%(log_color)s[%(levelname)s] %(message)s', log_colors=colors)
    except:
        pass
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def set_color(c):
    global last_color
    logger.info('Setting blync color to {0}'.format(c))
    blynux_bin = spawn.find_executable('blynux')
    cmd = [blynux_bin, '--device', '0', '--color', c]
    subprocess.call(cmd)
    if 'OFF' not in c:
        last_color = c
    logger.info('Last color is now {0}'.format(last_color))

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

try:
    set_color('green')
    while True:
        if screensaver_active():
            if not ssaver:
                logger.info('Screensaver is now active, disabling blync')
                set_color('OFF')
                ssaver = True
            time.sleep(sleep_interval)
            continue
        elif ssaver:
            logger.info('Screensaver is now inactive')
            ssaver = False
            set_color(last_color)

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
    logger.info('KeyboardInterrupt received')
    pass
except Exception, e:
    logger.error('Exception caught: {0}'.format(str(e)))

logger.info('Terminating')
