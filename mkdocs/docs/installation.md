# SatLink Installation

SatLink needs a Python 3 installation to run. It is recommended an environment with python 3.9.

You can download Python in [python.org](https://www.python.org/downloads/).

To install, just copy all the folders and files to any directory and make sure all packages/libraries are installed.

## Packages

SatLink has dependencies and needs some packages to run. They are: [itur](https://pypi.org/project/itur/#description),
[Numpy](https://numpy.org/), [tqdm](https://github.com/tqdm/tqdm), [pathos](https://github.com/uqfoundation/pathos),
[pandas](https://pandas.pydata.org/), [Astropy](https://www.astropy.org/).

One can install SatLink simply by running **first_setup.py**. It will install all the required packages.

Alternatively, run the following command:
    
    pip install -r requirements.txt

If an IDE, like [PyCharm](https://www.jetbrains.com/pt-br/pycharm/), 
is being used, it will automatically detect the requirements file and ask to install the packages.

Lastly, the packages can be installed individually. Here's the code with the currently tested versions:

    pip install itur==0.4.0
    pip install tqdm==4.66.5
    pip install pandas==2.2.3
    pip install pathos==0.3.3
    pip install astropy==6.1.4
    pip install matplotlib==3.9.2

##Using SatLink
Use the example files like `single_point_example.py` and `multi_point_example.py` to get started.

For more detailed information about the code-based functions and classes, please refer to [Code-based usage](code_use.md).