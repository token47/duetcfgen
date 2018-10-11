#!/usr/bin/python3

# Duet config generator, by Andre Ruiz <andre.ruiz@gmail.com>
# Please contribute at https://github.com/token47/duetcfgen

import sys, os, re, shutil
import tomlkit as toml
import jinja2, ftptool

root_dir = os.path.dirname(sys.argv[0]) or '.'
build_dir = "build"
backup_dir = "backup"
comment_column = 50

def load_variables(rootdir, filename):

    with open(rootdir + '/' + filename,'r',encoding='utf-8') as f:
        variables = toml.parse(f.read())
    return variables

def load_template(rootdir, filename, variables):

    j2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(rootdir),
        trim_blocks=True)
    return j2_env.get_template(filename).render(variables)

def switch_cfg_file(name):

    global outputfd

    if outputfd:
        outputfd.close()
    if name:
        create_dir(build_dir + '/' + os.path.dirname(name))
        log_normal('generating ' + name)
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
        log_error('Tried to write without opening a file first, check template')

def create_dir(dirname):

    os.makedirs(dirname, exist_ok=True)

def initialize_build_dir():
    log_normal("Cleaning build dir")
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    create_dir(build_dir)

def initialize_backup_dir():
    log_normal("Cleaning backup dir")
    if os.path.isdir(backup_dir):
        shutil.rmtree(backup_dir)
    create_dir(backup_dir)

def log_error(msg):

    print('ERROR: ' + msg)
    sys.exit(1)

def log_normal(msg):

    print('LOG: ' + msg)

def generate_config():

    initialize_build_dir()
    for line in rendered.split("\n"):
        if re.match("#", line): continue
        if re.fullmatch("[ \t]*", line): continue
        f = re.fullmatch("@file[ \t]+(?P<file>.*)", line)
        if f:
            switch_cfg_file(f.group("file"))
            continue
        write_cfg_line(line)

def connect_ftp():

    global duet_ftp

    log_normal("connecting to the Duet by FTP")
    try:
        duet_ftp = ftptool.FTPHost.connect(variables['net']['ip_address'], user="duet", password=variables['printer']['password'], timeout=10)
    except Exception as e:
        log_error("Could not connect to duet. Reason: " + str(e))

def disconnect_ftp():

    global duet_ftp

    duet_ftp.quit()


def upload_by_ftp():

    global duet_ftp

    duet_ftp.mirror_to_remote(build_dir, "/")

def download_by_ftp():

    global duet_ftp

    initialize_backup_dir()
    duet_ftp.mirror_to_local("/", backup_dir)
    

variables = load_variables(root_dir, "variables.toml")
rendered = load_template(root_dir, "template.jinja", variables)
outputfd = None
duet_ftp = None

generate_config()
connect_ftp()
download_by_ftp()
upload_by_ftp()
disconnect_ftp()

