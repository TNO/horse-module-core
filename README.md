# Horse Augmented Reality

Also see
- [Horse](http://www.horse-project.eu/)
- [TNO](https://tno.nl)


## Installation

For Unix one can use the docker file for installation.


# Install python and packages

For Windows we recommend [Anaconda](https://www.continuum.io/downloads) as an easy way to get most of the dependencies out-of-the-box.

For conda use the following commands:
```
> conda install -y scipy spyder qtpy matplotlib zmq pandas scikit-image pyqtgraph colorama lxml
> conda install -y -c conda-forge opencv
> pip install attrs transitions apscheduler websocket-client jsonpickle
```

# Install the source code

The source code can be obtained from gitlab.
```
git clone https://ci.tno.nl/gitlab/HORSE/horseAR.git
```
The horseAR packages then have be be installed:
```
> cd [SOURCEDIR]
> python setup.py develop  
```

# Install OPS

???

# Install Horse message server



# (optional) Install artno

Needed for calibration.


## Usage

See the wiki on Gitlab.

## License

See [License](LICENSE.txt)
