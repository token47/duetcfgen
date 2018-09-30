# duetcfgen
Duet Config Generator

What this is NOT:

- attempt to negate the RRF "All Gcode" filosophy
- an attempt to create a Configuration.h (a la Marlin) for RRF

What this IS:

- a way to quickly edit all the files on the same place
- a way to use variables for repetitive information
- a way to use "vim" on my linux instead of the web editor

It will:

- compile a template, generating all the individual files
- do variable replacement while compiling
- upload all of them to the duet using ftp
- optionally will reset the duet after uploading
- can potentially download a backup of all files before uploading (currently broken)

And...

- download is not working, for some reason an "mget *" freezes RRF's ftp
- upload sometimes fail, if you run again it will work. there is some issue with RRF's ftp, looking into it
- there are no command line options yet, please comment/uncomment the funcions inside the script
- it's shell, it's fragile, it's a hack. use with caution.

I'm using it for a few days and liking it a lot. It is really productive, specially when building the printer and doing all sorts of calibrations and configurations for the first time.

Sugestions are welcome.

PS: please ignore the .py, .toml and .jinja files for now, it's an ongoing port to python, not yet functional.

