# Based on: https://github.com/albertosottile/darkdetect
#-----------------------------------------------------------------------------
#  Copyright (C) 2019 Alberto Sottile
#
#  Distributed under the terms of the 3-clause BSD License.
#-----------------------------------------------------------------------------

# currently system detect only supports linux GTK
# non-supported OS will return dark mode by default

def _default_theme():
    return "Dark"

import sys

def detect():
    if sys.platform == "linux":
        import subprocess
        # Here we just triage to GTK settings for now
        try:
            out = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True)
            stdout = out.stdout.decode()
        except Exception:
            return _default_theme()
        # we have a string, now remove start and end quote
        theme = stdout.lower().strip()[1:-1]
        if theme.endswith('-dark'):
            return "Dark"
        else:
            return "Light"

    else:
        return _default_theme()
