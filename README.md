<!-- This template was took from https://github.com/othneildrew/Best-README-Template -->

<!-- PROJECT SHIELDS -->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL3 License][license-shield]][license-url]
[![Documentation Status][docs-shield]][docs-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/ziotom78/instrumentdb">
    <img src="images/logo.svg" alt="Logo" width="180">
  </a>

  <h3 align="center">InstrumentDB</h3>

  <p align="center">
    A RESTful database to manage specifications of complex scientific instruments
    <br />
    <a href="https://instrumentdb.readthedocs.io/en/latest/?badge=latest"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ziotom78/instrumentdb">View Demo</a>
    ·
    <a href="https://github.com/ziotom78/instrumentdb/issues">Report Bug</a>
    ·
    <a href="https://github.com/ziotom78/instrumentdb/issues">Request Feature</a>
  </p>
</p>



## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/ziotom78/instrumentdb)


### Built With

-   [Python 3](https://www.python.org/)
-   [Django 4](https://www.djangoproject.com/) & [Django REST
  framework](https://www.django-rest-framework.org/) & [Django
  MPTT](https://github.com/django-mptt/django-mptt)
-   [SQLite](https://sqlite.org)



## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

You must have Python 3; it is advised to create a virtual environment
before installing InstrumentDB.

### Installation
 
1.  Clone the repo:
    ```sh
    git clone https://github.com/ziotom78/instrumentdb.git && cd instrumentdb
    ```
    
2.  Install all the dependencies using `poetry`:

    ```sh
    poetry install
    ```

3.  Create a custom configuration file and customize it. Be sure to put some random password in `SECRET_KEY`!
    ```sh
    cp .env.example .env && vim .env
    ```
    
4.  Create the database
    ```sh
    poetry run python3 manage.py migrate
    ```

5.  Create a superuser
    ```sh
    poetry run python3 manage.py createsuperuser
    ```

6.  Fire up the web server
    ```sh
    poetry run python3 manage.py runserver
    ```

7.  Connect to http://127.0.0.1:8000/ and enjoy!


## Usage

See the [documentation][docs-url].


## Roadmap

See the [open issues](https://github.com/ziotom78/instrumentdb/issues)
for a list of proposed features (and known issues).



## Contributing

Contributions are what make the open source community such an amazing
place to be learn, inspire, and create. Any contributions you make are
**greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Usage


## License

Distributed under the GPL3 License. See [`LICENSE.md`][license-url]
for more information.



## Contact

Maurizio Tomasi -
[@MaurizioTomasi2](https://twitter.com/@MaurizioTomasi2) -
ziotom78{at}gmail.com

Project Link:
[https://github.com/ziotom78/instrumentdb](https://github.com/ziotom78/instrumentdb)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

- The LiteBIRD Instrument Model team for many ideas: Sophie Henrot-Versillé, Hirokazu Ishino, Tomotake Matsumura.

- The ASI (Agenzia Spaziale Italiana) SSDC Team for testing the code: Fabrizio Fabri, Antonio Guerra, Gemma Luzzi, Daniele Navarra, Gianluca Polenta


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[forks-shield]: https://img.shields.io/github/forks/ziotom78/instrumentdb.svg?style=flat-square
[forks-url]: https://github.com/ziotom78/instrumentdb/network/members
[stars-shield]: https://img.shields.io/github/stars/ziotom78/instrumentdb.svg?style=flat-square
[stars-url]: https://github.com/ziotom78/instrumentdb/stargazers
[issues-shield]: https://img.shields.io/github/issues/ziotom78/instrumentdb.svg?style=flat-square
[issues-url]: https://github.com/ziotom78/instrumentdb/issues
[license-shield]: https://img.shields.io/github/license/ziotom78/instrumentdb.svg?style=flat-square
[license-url]: https://github.com/ziotom78/instrumentdb/blob/master/LICENSE.md
[product-screenshot]: images/instrumentdb-screenshot.png
[docs-shield]: https://readthedocs.org/projects/instrumentdb/badge/?version=latest
[docs-url]: https://instrumentdb.readthedocs.io/en/latest/?badge=latest
