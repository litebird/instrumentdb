# HEAD

-   Add the variable `CSRF_TRUSTED_ORIGINS` to the list of fields in the `.env` file [#115](https://github.com/ziotom78/instrumentdb/pull/115)

-   Remove limit in number of fields within a POST request [#114](https://github.com/ziotom78/instrumentdb/pull/114)

-   Fix the path to data files that is shown in the “Details” page [#113](https://github.com/ziotom78/instrumentdb/pull/113)

-   Fix an error in `manage.py export` when plot files are present [#112](https://github.com/ziotom78/instrumentdb/pull/112)

-   Be more robust against `git`'s output [#111](https://github.com/ziotom78/instrumentdb/pull/111)

-   Better handle missing `metadata` fields in data files [#110](https://github.com/ziotom78/instrumentdb/pull/110)

-   Properly delete files that are no longer referenced in the database [#109](https://github.com/ziotom78/instrumentdb/pull/109)

-   Allow empty metadata in data files when using the RESTful API [#107](https://github.com/ziotom78/instrumentdb/pull/107)

-   Implement Swagger and Redoc web pages documenting the RESTful API [#106](https://github.com/ziotom78/instrumentdb/pull/106)

-   Validate entity/quantity names in forms and RESTful API [#102](https://github.com/ziotom78/instrumentdb/pull/102), [#105](https://github.com/ziotom78/instrumentdb/pull/105)

-   Make the `export` and `import` commands more robust, fix bugs, and make release documents exported as well [#101](https://github.com/ziotom78/instrumentdb/pull/101)

-   Add the switches `--skip-empty-quantities` and `--skip-empty-entities` to the `export` command [#100](https://github.com/ziotom78/instrumentdb/pull/100)

-   Add a new API to access entities and quantities through their path [#98](https://github.com/ziotom78/instrumentdb/pull/98), [#108](https://github.com/ziotom78/instrumentdb/pull/108)

-   Make the download of specification documents easier [#97](https://github.com/ziotom78/instrumentdb/pull/97)

-   Implement release documents, support Django 4 [#96](https://github.com/ziotom78/instrumentdb/pull/96)

-   The URL `/api/releases` now uses pagination [#95](https://github.com/ziotom78/instrumentdb/pull/95)

-   The tree of entities is now collapsible [#94](https://github.com/ziotom78/instrumentdb/pull/94)

-   Extend test coverage, fix issues in the code [#93](https://github.com/ziotom78/instrumentdb/pull/93)

-   Validate the `metadata` field of data files [#92](https://github.com/ziotom78/instrumentdb/pull/92)

-   Implement the `delete-all` command [#91](https://github.com/ziotom78/instrumentdb/pull/91), [#103](https://github.com/ziotom78/instrumentdb/pull/103)

-   Implement the `delete-data-files` command [#90](https://github.com/ziotom78/instrumentdb/pull/90)

-   Clean up the documentation [#89](https://github.com/ziotom78/instrumentdb/pull/89)

-   Raise a HTTP 404 error if the user asks to download a file that was not uploaded to the database [#87](https://github.com/ziotom78/instrumentdb/pull/87)

-   Let the user change their own passwords [#85](https://github.com/ziotom78/instrumentdb/pull/85)

# Version 1.1.0

-   Make the code easier to customize [#83](https://github.com/ziotom78/instrumentdb/pull/83)

-   Add the ability to send log messages to the console [#80](https://github.com/ziotom78/instrumentdb/pull/80)

-   Stop using the old `uuid` external package [#79](https://github.com/ziotom78/instrumentdb/pull/79)

-   Add the ability to enable logging [#78](https://github.com/ziotom78/instrumentdb/pull/78)

-   Add the `--only-tree` switch to the `export` command [#77](https://github.com/ziotom78/instrumentdb/pull/77)

-   Remove LiteBIRD-related stuff [#76](https://github.com/ziotom78/instrumentdb/pull/76)

# Version 1.0.2

-   Fix permissions in the Home page [#71](https://github.com/ziotom78/instrumentdb/pull/71)

# Version 1.0.1

-   Prevent code crashes when the storage directory is outside the source path [#69](https://github.com/ziotom78/instrumentdb/pull/69)

# Version 1.0.0

-   Make the "export" command able to download just one release [#63](https://github.com/ziotom78/instrumentdb/pull/63)

# Version 0.5.1

-   Fix broken dependencies in `pyproject.toml` and `requirements.txt`

# Version 0.5.0

-   Add RESTful API to upload data files and plot files [#60](https://github.com/ziotom78/instrumentdb/pull/60)

-   Bump django from 3.2.4 to 3.2.5 [#52](https://github.com/ziotom78/instrumentdb/pull/52)
-    
-   Add dependency on [sslserver](https://github.com/teddziuba/django-sslserver) [#47](https://github.com/ziotom78/instrumentdb/pull/47)

-   Authentication has been fully implemented [#39](https://github.com/ziotom78/instrumentdb/pull/39)

# Version 0.4.2

-   Explain how to install InstrumentDB without Poetry in the README.

# Version 0.4.1

-   Add link to the «Releases» page in the top bar and some more release information to the data file view [#40](https://github.com/ziotom78/instrumentdb/pull/40)

-   Fix bug [#37](https://github.com/ziotom78/instrumentdb/issues/37)

# Version 0.4.0

-   Fix bug [#33](https://github.com/ziotom78/instrumentdb/issues/33)

# Version 0.3.1

-   Fix bug [#31](https://github.com/ziotom78/instrumentdb/issues/31)

# Version 0.3.0

-   Fix bug [#29](https://github.com/ziotom78/instrumentdb/issues/29)
-   Implement API to access releases [#30](https://github.com/ziotom78/instrumentdb/pull/30)

# Version 0.2.0

-   Make JSON the default format when importing/exporting the database [PR#28](https://github.com/ziotom78/instrumentdb/pull/28)

-   Format JSON records and highlight their syntax using [Highlight.js](https://highlightjs.org/) ([PR#27](https://github.com/ziotom78/instrumentdb/pull/27))

-   Increase the size of the `metadata` field for data files from 8 kB to 32 kB 
    [0cf6cb](https://github.com/ziotom78/instrumentdb/commit/0cf6cb83766696c5471dc5ba74d14ba5d709a8f0)

# Version 0.1.0

- First release
