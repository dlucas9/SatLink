# SatLink

<img src="pics/LogoSatLink225_225_white.png" alt="logo" width="150"/>

SatLink is a python based application that runs specific satellite downlink calculations. Its main functions are:

  - Atmospheric attenuation calculation (via [itur])
  - Single and multi-point downlink availability calculation (input and output csv file)
  - Antenna size estimation for a desired availability (single point analysis and multi point csv output)
  - **REST API for programmatic access to all calculation functions**
  - Save and load parameters for satellites, ground stations and reception characteristics
  - Totally free !!!

This project is an attempt to simplify satellite's link budget calculations and to create a tool for teaching purposes. Please check the [**documentation**](https://cfragoas.github.io/SatLink/) for more detailed information.

## Usage Options

SatLink can be used in multiple ways:

1. **Command Line**: Direct Python script execution using the example files
2. **REST API**: HTTP API server for integration with other applications (see [API_USAGE.md](API_USAGE.md))
3. **Web App**: Streamlit-based web interface using **satlink_web.py** (requires [streamlit](https://streamlit.io/))
4. **Docker**: Containerized deployment using the provided [Dockerfile](Dockerfile)

# Using SatLink via python commands 
 SatLink consists of three main classes 
 
  - Satellite class
  - Ground Station class
  - Reception class

You need to define those three objects and set their relationship
```sh
from GrStat import GroundStation, Reception
from sat import Satellite

# creating the objects
station = GroundStation(site_lat, site_long)
sat = Satellite(sat_long, freq, eirp_max, hsat, b_transponder, b_util, _, _, mod, rolloff, fec)
receptor = Reception(ant_size, ant_eff, coupling_loss, polarization_loss, lnb_gain, lnb_noise_temp, cable_loss, desfoc_max)

# relating the objets to the satellite
sat.set_grstation(station)
sat.set_reception(receptor) 

# example - calcullating the link availability
availability = sat.get_availability()
print(availability)  # 0 - 100 percentage

# example - calcullating the power flux density in the reception point and the antenna noise in rain conditions
pw_flx = sat.get_power_flux_density()
print(pw_flx)  # watts/m²
ant_noise = sat.reception.get_antenna_noise_temp()
print(ant_noise)  # Kelvin
ant_noise_rain = sat.get_antenna_noise_rain()
print(ant_noise_rain)  # Kelvin
```

The other functions are detailed in the [**documentation**](https://cfragoas.github.io/SatLink/).

# Using SatLink REST API

SatLink provides a comprehensive REST API for integration with other applications. Start the API server:

```bash
python satlink_api.py
```

The API will be available at `http://localhost:5000` and provides four main endpoints:

- `POST /api/single-point` - Single point link budget calculation
- `POST /api/multi-point` - Multi-point availability calculation  
- `POST /api/single-point-antenna-size` - Single point antenna sizing analysis
- `POST /api/multi-point-antenna-size` - Multi-point antenna sizing analysis

For detailed API usage examples and parameter descriptions, see [API_USAGE.md](API_USAGE.md).

**For Frontend Developers**: See the comprehensive [Frontend API Manual](FRONTEND_API_MANUAL.md) for detailed integration guidelines, form templates, error handling, and complete JavaScript examples.

Example API call:
```bash
curl -X POST http://localhost:5000/api/single-point \
  -H "Content-Type: application/json" \
  -d '{
    "sat_long": -70, "freq": 12, "eirp": 54,
    "b_transponder": 36, "b_util": 9,
    "mod": "8PSK", "fec": "120/180",
    "site_lat": -3.7, "site_long": -45.9
  }'
```

### Libraries

SatLink uses a bunch of different open source python libraries

* [itur] - A python implementation of the ITU-R P. Recommendations to compute atmospheric attenuation in slant and horizontal paths
* [pyqt] - PyQt is a set of Python bindings for The Qt Company's Qt application framework
* [tqdm] - Instantly make your loops show a smart progress meter
* [pathos] - It provides a consistent high-level interface for configuring and launching parallel computations across heterogeneous resources.
* [pandas] - Fast, powerful, flexible and easy to use open source data analysis and manipulation tool
* [astropy] - Common core package for Astronomy in Python and foster an ecosystem of interoperable astronomy packages
* [numpy] - The fundamental package for scientific computing with Python

### Installation

SatLink has only been tested in python 3.
Just copy all the folders and files to any directory and make sure all packages and dependencies are installed. For Linux users, be sure to install the required packages with the following one-liner (or the equivalent command in your current distribution):

```sh
sudo apt install build-essentials gcc g++ python3-pyqt5
```

For installing the Python packages, just run **first_setup.py** located in the main SatLink folder for a fresh package installation. Alternatively you can run the following command:

```sh
pip install -r requirements.txt
```

or

```sh
pip install numpy==1.26.4
pip install itur==0.4.0
pip install tqdm==4.66.5
pip install pandas==2.2.3
pip install pathos==0.3.3
pip install astropy==6.1.4
pip install matplotlib==3.9.2
pip install chardet==5.2.0
```

To use SatLink, import the required classes and run the example files. Check the example files like `single_point_example.py` and `multi_point_example.py` for usage instructions.

### Contributions

Since this is still a early version of the code, we expect there some problem can be found, We are tottaly open for contributions and bug/problems reports. **Please tell us!**

### Future Developments

Some updates are planned for the future of the SatLink

* Worst month availabilty calcullation
* Web application
* Map function
* More robust XPD calculations

### Authorship

All the code development was made by Christian Rodrigues.

Contact: christianfragoas@gmail.com

### Credits

[Globo] - For supporting the very first release version of the application

[Caio Alexandre] - Logo designer


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [Globo]: <https://globoplay.globo.com/>
   [itur]: <https://github.com/iportillo/ITU-Rpy>
   [pathos]: <https://github.com/uqfoundation/pathos>
   [tqdm]: <https://github.com/tqdm/tqdm>
   [pandas]: <https://pandas.pydata.org/>
   [astropy]: <https://www.astropy.org/>
   [numpy]: <https://numpy.org/>
   [pyqt]: <https://riverbankcomputing.com/software/pyqt/intro>
   [Caio Alexandre]: <https://www.instagram.com/caioalexandredasilva>   
