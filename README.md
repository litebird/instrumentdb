<!-- This template was took from https://github.com/othneildrew/Best-README-Template -->

<!-- *** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo, twitter_handle, email
-->


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL3 License][license-shield]][license-url]
[![Documentation Status][docs-shield]][docs-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/litebird/instrumentdb">
    <img src="images/logo.svg" alt="Logo" width="180">
  </a>

  <h3 align="center">InstrumentDB</h3>

  <p align="center">
    A RESTful database to manage specifications of complex scientific instruments
    <br />
    <a href="https://instrumentdb.readthedocs.io/en/latest/?badge=latest"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/litebird/instrumentdb">View Demo</a>
    ·
    <a href="https://github.com/litebird/instrumentdb/issues">Report Bug</a>
    ·
    <a href="https://github.com/litebird/instrumentdb/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
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



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/litebird/instrumentdb)


### Built With

-   [Python 3](https://www.python.org/)
-   [Django 3](https://www.djangoproject.com/) & [Django REST
  framework](https://www.django-rest-framework.org/) & [Django
  MPTT](https://github.com/django-mptt/django-mptt)
-   [SQLite](https://sqlite.org)



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

You must have Python 3; it is advised to create a virtual environment
before installing InstrumentDB.

### Installation
 
1.  Clone the repo:
    ```sh
    git clone https://github.com/litebird/instrumentdb.git && cd instrumentdb
    ```
    
2.  Install all the dependencies using `poetry`
    ```sh
    pip install -r requirements.txt
    ```

3.  Create a custom configuration file and customize it. Be sure to
    put some random password in `SECRET_KEY`!
    ```sh
    cp .env.example .env && vim .env
    ```
    
3.  Create the database
    ```sh
    ./manage.py migrate
    ```

4.  Create a superuser
    ```sh
    ./manage.py createsuperuser
    ```

4.  Fire up the web server
    ```sh
    ./manage.py runserver
    ```

5.  Connect to http://127.0.0.1:8000/ and enjoy!


### Developer installation

Developers willing to hack instrumentdb should install
[Poetry](https://python-poetry.org/). I developed InstrumentDB under
Linux Manjaro and Linux Mint 20.1, but it should be usable on other
platforms too (Windows, Mac OS X, FreeBSD, …).

To install Poetry, see
[here](https://python-poetry.org/docs/#installation).


1.  Clone the repo:
    ```sh
    git clone https://github.com/litebird/instrumentdb.git && cd instrumentdb
    ```
    
2.  Install all the dependencies using `poetry`
    ```sh
    poetry install
    ```

3.  Create a custom configuration file and customize it. Be sure to
    put some random password in `SECRET_KEY`!
    ```sh
    cp .env.example .env && vim .env
    ```
    
3.  Create the database
    ```sh
    poetry run manage.py migrate
    ```

4.  Create a superuser
    ```sh
    poetry run manage.py createsuperuser
    ```

4.  Fire up the web server
    ```sh
    poetry run manage.py runserver
    ```

5.  Connect to http://127.0.0.1:8000/ and enjoy!


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be
used. Additional screenshots, code examples and demos work well in
this space. You may also link to more resources.

For more examples, please refer to the [documentation][docs-url].


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/litebird/instrumentdb/issues)
for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing
place to be learn, inspire, and create. Any contributions you make are
**greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the GPL3 License. See [`LICENSE.md`][license-url]
for more information.



<!-- CONTACT -->
## Contact

Maurizio Tomasi -
[@MaurizioTomasi2](https://twitter.com/@MaurizioTomasi2) -
litebird{at}gmail.com

Project Link:
[https://github.com/litebird/instrumentdb](https://github.com/litebird/instrumentdb)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

- The LiteBIRD Instrument Model team for many ideas: Sophie
  Henrot-Versillé, Hirokazu Ishino, Tomotake Matsumura.



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[forks-shield]: https://img.shields.io/github/forks/litebird/instrumentdb.svg?style=flat-square
[forks-url]: https://github.com/litebird/instrumentdb/network/members
[stars-shield]: https://img.shields.io/github/stars/litebird/instrumentdb.svg?style=flat-square
[stars-url]: https://github.com/litebird/instrumentdb/stargazers
[issues-shield]: https://img.shields.io/github/issues/litebird/instrumentdb.svg?style=flat-square
[issues-url]: https://github.com/litebird/instrumentdb/issues
[license-shield]: https://img.shields.io/github/license/litebird/instrumentdb.svg?style=flat-square
[license-url]: https://github.com/litebird/instrumentdb/blob/master/LICENSE.md
[product-screenshot]: images/instrumentdb-screenshot.png
[docs-shield]: https://readthedocs.org/projects/instrumentdb/badge/?version=latest
[docs-url]: https://instrumentdb.readthedocs.io/en/latest/?badge=latest
