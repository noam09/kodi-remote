#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
try:
    from curtsies import Input
except ImportError:
    print('Missing module curtsies')
    exit()
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

# Get configuration
script_dir = os.path.dirname(__file__)
config = SafeConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))

# Check if player parameter set
if len(sys.argv) != 2:
    print('Missing host name. Hosts configured:')
    for section in config._sections:
        print('\t - {}'.format(section))
    exit()

# Check if player parameter is configured
if sys.argv[1] not in config._sections:
    print('Invalid host name. Hosts configured:')
    for section in config._sections:
        print('\t - {}'.format(section))
    exit()
else:
    player_name = sys.argv[1]

# Set player configuration
player = {'host': config.get(player_name, 'ip'),
          'port': config.get(player_name, 'port'),
          'username': config.get(player_name, 'user'),
          'password': config.get(player_name, 'pass')}

# JSON-RPC URL
API_URL = 'http://{}:{}/jsonrpc'

# Display key values
verbose = False


def api(device, method, params=None):
    """ Call JSON-RPC API for specified device,
    using method and optional parameters """
    query = {"id": "1",
             "jsonrpc": "2.0",
             "method": method}
    if params:
        query['params'] = params
    try:
        r = requests.post(API_URL.format(device['host'], str(device['port'])),
                          data=json.dumps(query),
                          auth=HTTPBasicAuth(device['username'], device['password']))
    except ConnectionError as e:
        print('Exception: {}'.format(str(e)))
        print('Probably invalid host or port')
        return False
    except Exception as e:
        print('Exception: {}'.format(str(e)))
        return False
    if r:
        res = json.loads(r.text)
        # print(res)
        return res
    else:
        if r.status_code == 401:
            print('Invalid user/password')
            return False


def key(device, key):
    if key == 'right':
        r = api(device, "Input.Right")
    elif key == 'left':
        r = api(device, "Input.Left")
    elif key == 'up':
        r = api(device, "Input.Up")
    elif key == 'down':
        r = api(device, "Input.Down")
    elif key == 'select':
        r = api(device, "Input.Select")
    elif key == 'back':
        r = api(device, "Input.Back")
    elif key == 'menu':
        r = api(device, "Input.ContextMenu")
    return r


def main():
    try:
        with Input(keynames='curses') as input_generator:
            for e in input_generator:
                if verbose:
                    print(repr(e))
                if e == 'KEY_LEFT':
                    key(player, 'left')
                if e == 'KEY_RIGHT':
                    key(player, 'right')
                if e == 'KEY_UP':
                    key(player, 'up')
                if e == 'KEY_DOWN':
                    key(player, 'down')
                if e == '\n':
                    key(player, 'select')
                if e == '\x7f':
                    key(player, 'back')
                if e == 'c':
                    key(player, 'menu')
                # Quit
                if e == 'q':
                    break
                # ESC
                if e == '\x1b':
                    break
    # CTRL-C
    except KeyboardInterrupt:
        pass
    print('Quitting...')
    exit()

if __name__ == '__main__':
    main()
