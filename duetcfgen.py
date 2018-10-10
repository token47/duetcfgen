#!/usr/bin/python3

# Duet config generator, by Andre Ruiz <andre.ruiz@gmail.com>

import sys, os, re, shutil
import tomlkit as toml
import jinja2

build_dir = './build2'
comment_column = 50

def load_variables(filename):

    with open((os.path.dirname(sys.argv[0]) or '.') + '/' + filename,'r',encoding='utf-8') as f:
        variables = toml.parse(f.read())

    return variables

def load_template(filename, variables):

    j2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(sys.argv[0]) or '.'),
        trim_blocks=True)

    return j2_env.get_template(filename).render(variables)

def switch_cfg_file(name):

    global outputfd

    if outputfd:
        outputfd.close()
    if name:
        create_dir(build_dir + '/' + os.path.dirname(name))
        log_normal('writing ' + name)
        outputfd = open(build_dir + '/' + name, 'w')

def write_cfg_line(text):

    if outputfd:
        e = re.fullmatch("(?P<command>[^;]*)?(?P<comment>;.*)?", text)
        command = e.group("command") or ''
        comment = e.group("comment") or ''
        command = command.strip()
        comment = comment.strip()
        if command:
            l = len(command)
            if l < comment_column: command += " " * (comment_column - l)
            comment = ' ' + comment
        outputfd.write(command + comment + '\n')
    else:
        log_error('Tried to write without opening a file')

def create_dir(dirname):

    os.makedirs(dirname, exist_ok=True)

def initialize_build_dir():
    log_normal("Cleaning build dir")
    shutil.rmtree(build_dir)
    create_dir(build_dir)

def log_error(msg):

    print('ERROR: ' + msg)

def log_normal(msg):

    print('LOG: ' + msg)

def write_config():

    for line in rendered.split("\n"):

        if re.match("#", line): continue

        if re.fullmatch("[ \t]*", line): continue
        
        f = re.fullmatch("@file[ \t]+(?P<file>.*)", line)
        if f:
            switch_cfg_file(f.group("file"))
            continue
        
        write_cfg_line(line)


variables = load_variables("variables.toml")
rendered = load_template("template.jinja", variables)
outputfd = None

initialize_build_dir()
write_config()

