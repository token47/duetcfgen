#!/bin/bash

# Duet Configuration Generator v:0.1
# By Andre Ruiz <andre.ruiz@gmail.com>

set -u
set -e

FILE_VARIABLES="./variables.cfg"
FILE_TEMPLATE="./template.cfg"
BUILDDIR="./build"
BACKUPDIR="./backup"

log() {
	echo "LOG: $*" 2>&1
}

logerror() {
	echo "ERROR: $*" 2>&1
	exit 255
}

create_build_dir() {
	rm -rf "$BUILDDIR"
	mkdir "$BUILDDIR"
}

create_backup_dir() {
	rm -rf "$BACKUPDIR"
	mkdir "$BACKUPDIR"
}

create_subdir() {
	subdir="$1"
	[ ! -d "$subdir" ] && mkdir "$subdir" || :
}

upload_by_ftp() {
	log "uploading to the board by FTP"
	ftp -in $DUET_IP_ADDRESS <<-EOF
		user duet ${PRINTER_PASSWORD:-nopasswd}
		cd /sys
		lcd ${BUILDDIR}/sys
		mput *
		cd /macros
		lcd ../../${BUILDDIR}/macros
		mput *
		bye
	EOF
}

download_by_ftp() {
	log "downloading from the board by FTP (backup)"
	create_subdir "./$BACKUPDIR/sys/"
	create_subdir "./$BACKUPDIR/macros/"
	ftp -in $DUET_IP_ADDRESS <<-EOF
		user duet ${PRINTER_PASSWORD:-nopasswd}
		cd /sys
		lcd ${BACKUPDIR}/sys
		mget *
		cd /macros
		lcd ../../${BACKUPDIR}/macros
		mget *
		bye
	EOF
}

reboot_duet_by_telnet() {
	log "rebooting the Duet"
	expect <<-EOF
		spawn telnet "$DUET_IP_ADDRESS"
		expect "Please enter your password:"
		expect "> "
		send "${PRINTER_PASSWORD}\r"
		expect "Log in successful!"
		send "M999\r"
	EOF

}

parse_template_file() {
	filename=""
        tempfile=$(mktemp ./templateXXXXXX.tmp)
        echo 'cat <<END_TEMPLATE' > "$tempfile"
        cat "$FILE_TEMPLATE" >> "$tempfile"
        echo 'END_TEMPLATE' >> "$tempfile"
        source $tempfile | \
		sed -e '/^#/d' -e 's/;.*$//' -e '/^[    ]*$/d' | \
		while read line; do
		if [[ "$line" =~ ^@file\ ([^\ \	]+) ]]; then
		       	filename="${BASH_REMATCH[1]}"
			log "generating $BUILDDIR/$filename"
			create_subdir "$BUILDDIR/$(dirname $filename)"
			touch "$BUILDDIR/$filename"
			continue
		fi
		echo $line >> "$BUILDDIR/$filename"
	done
        rm -f "$tempfile"

}

source "$FILE_VARIABLES"
source ~/.duetcfgenvars

log "creating build dir"
create_build_dir
log "parsing template file"
parse_template_file
log "copying variables and template to sys dir (backup)"
cp "$FILE_VARIABLES" "$FILE_TEMPLATE" "$BUILDDIR"/sys/
#download_by_ftp
upload_by_ftp
#reboot_duet_by_telnet
log "finished"

