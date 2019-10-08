## PMRL

> Python Meetup Roguelike

A little game I wrote for a talk on roguelike game development in Python at PyATL.

## Development

### First time setup

```
python3 -m venv ./env
source env/bin/activate
# Now that you're in your virtual environment...
pip install -r requirements.txt
```

### Upgrade dependencies

```
# In your virtual environment...
pip install --upgrade -r requirements
```

## Building Executables

PyInstaller is used to create an distributable bundle containing an executable
that can be run without downloading Python, installing libraries, etc.

```
# In your virtual environment...
pyinstaller pmrl.py
```

After the PyInstaller build finishes, the _dist/pmrl_ directory will contain the
application and all dependencies necessary to run the game on the platform you
ran the build on.
