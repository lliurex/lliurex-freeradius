#!/bin/bash

cp ../install/usr/sbin/lliurex-freeradius /tmp/lliurex-freeradius.py

xgettext ../install/usr/share/lliurex-freeradius/rsrc/lliurex-freeradius.ui ../install/usr/share/lliurex-freeradius/*.py  -o lliurex-freeradius/lliurex-freeradius.pot

