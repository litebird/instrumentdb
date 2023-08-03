Commands
========

InstrumentDB implements a number of commands that can be executed from
the terminal. These are meant to ease the management of the database.

Here is the list:

- :ref:`export_cmd`
- :ref:`import_cmd`
- :ref:`updatedb_cmd`
- :ref:`deletedatafiles_cmd`

These commands can be executed from the command line using the syntax

.. code-block::

   python3 manage.py CMD

where ``CMD`` is the name of the command, e.g., ``export``. To get
help for the command, run

.. code-block::

   python3 manage.py CMD --help


.. _export_cmd:
``export``
----------

This command exports the content of the database into a folder.
The index of the database, all the metadata, the release information
and so on are stored in a file named ``schema.json``, while all the
data files, format specifications, plots, etc., are saved in separate
directories.

The purpose of the ``export`` command is to be paired with ``import``:
it enables a database to be created on a machine and replicated into
another.


.. _import_cmd:
``import``
----------

This command imports a JSON file and the associated files that have
been produced by the :ref:`_export_cmd` command.


.. _updatedb_cmd:
``updatedb``
------------

The database keeps a copy of every release in the form of a JSON file.
This command rebuilds all these JSON files. It should be triggered
if you fear that these files got corrupted.


.. _deletedatafiles_cmd:
``delete-data-files``
---------------------

Delete a set of data files from the database. You can specify a release tag
using the ``--release`` command-line switch: in this case, all the data files
belonging to the data release will be deleted. Any data file belonging to more
than one data release will be left untouched.