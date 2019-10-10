## PMRL

> Python Meetup Roguelike

A little game I wrote for a talk on roguelike game development in Python at PyATL.

## Development

### First time setup

Clone and enter the project directory:

```
git clone https://github.com/seansawyer/python-meetup-roguelike.git
cd python-meetup-roguelike
```

Then, if you are using pyenv:

```
pyenv virtualenv 3.7.4 pmrl-3.7.4
pyenv activate pmrl-3.7.4
pip install -r requirements.txt
```

Or if you are using your system Python (3.7+):

```
python3 -m venv ./env
source env/bin/activate
pip install -r requirements.txt
```

Now you may run the application:

```
# In your virtual environment...
python pmrl.py
```

### Upgrade dependencies

```
# In your virtual environment...
pip install --upgrade -r requirements.txt
```

## Building Executables

PyInstaller is used to create an distributable bundle containing an executable
that can be run without downloading Python, installing libraries, etc.

```
# In your virtual environment...
pyinstaller pmrl.py \
    --add-binary '/home/sean/src/python-meetup-roguelike/arial10x10.png:."
```

After the PyInstaller build finishes, the _dist/pmrl_ directory will contain the
application and all dependencies necessary to run the game on the platform you
ran the build on.

To run the packaged, standalone executable:

```
cd dist/pmrl
./pmrl
```
