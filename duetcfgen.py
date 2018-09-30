#!/usr/bin/python3

# Duet config generator, by Andre Ruiz <andre.ruiz@gmail.com>

import sys
import os
import tomlkit as toml

with open((os.path.dirname(sys.argv[0]) or '.') + '/variables.toml','r',encoding='utf-8') as f:
    variables = toml.parse(f.read())

print(variables)

