Web API
=======

This section provides the documentation to the web API implemented 

Format specifications
---------------------

You can query the list of format specifications by issuing a ``GET``
command to the url http://server/api/format_specs/. To get information
about one entity, append the full UUID and a slash to it:
http://server/api/format_specs/ede55e77-0dd1-483e-a307-e6e67759a450/.

To create a new entity, issue a ``POST`` command and pass a JSON
dictionary containing the following fields:

- ``document_ref``: a string uniquely identifying the document. The
  format of the string depends on the conventions used by the
  collaboration developing the instrument.
- ``title``: a string containing the title of the specification document.
- ``doc_file``: a file-like object containing the format specification document
- ``doc_file_name``: the file name to be suggested to the user when they want to download it
- ``doc_mime_type``: a string containing the MIME type of the specification document
- ``file_mime_type``: a string containing the MIME type of the file
  described by this specification document (optional).

Note the difference between ``doc_mime_type`` and ``file_mime_type``: the
former pertains to the *document* (DOCX, PDF, LaTeX, …), while the latter
refers to the *file* described by the specification document. Both are used
as hints to your browser: when you download the specification document
or the data file, letting your webbrowser know the MIME type can
enable more features, e.g., a preview within the “File save” dialog.

Here is an example, where we upload a Microsoft Word DOCX document describing
how to interpret an Excel file with the details of some electronic board::

  import requests as req

  server = "http://127.0.0.1:8000/"

  response = req.post(url=f"{server_url}/api/login",
      data={"username":"user1", "password": "passwd54321"}
  )
  assert response.ok
  auth_header = {"Authorization": "Token " + response.json()["token"]}

  response = req.post(
      server + "api/format_specs/",
      data={
          "document_ref": "DOC0001",
          "title": "Specification of the electronics",
          "doc_file_name": "DOC0001.docx",
          # The specification document is a MS Word file…
          "doc_mime_type": "application/vnd.openxmlformats-officedocument",
          # …which explains how to interpret the data file, created using MS Excel
          "file_mime_type": "application/vnd.openxmlformats-officedocument",
      },
      files={
          "doc_file": open("my_specification.docx", "rb"),
      }
      headers=auth_header,
  )
  assert response.ok
  print(response.json())


Entities
--------

You can query the list of entities by issuing a ``GET`` command to the
url http://server/api/entities/. To get information about one entity,
append the full UUID and a slash to it:
http://server/api/entities/ede55e77-0dd1-483e-a307-e6e67759a450/.

To create a new entity, issue a ``POST`` command and pass a JSON
dictionary containing the following fields:

- ``name``: a string
- ``parent``: the full URL to the parent entity; leave it out if the
  entity has no parent.
- ``children``: a list of full URLs for the child entities; you can
  leave it out.
- ``quantities``: a list of full URLs for each quantity belonging to
  this entity. Passing ``[]`` is ok.

Here is an example in Python, it creates a new entity and then deletes
it immediately after::

  import requests as req

  server = "http://127.0.0.1:8000/"

  response = req.post(url=f"{server_url}/api/login",
      data={"username":"user1", "password": "passwd54321"}
  )
  assert response.ok
  auth_header = {"Authorization": "Token " + response.json()["token"]}

  response = req.post(
      server + "api/entities/",
      data={
          "name": "my entity",
      },
      headers=auth_header,
  )
  assert response.ok
  print(response.json())

  # Output:
  # {'uuid': 'f89e8597-7561-4170-bec3-9837b3f32d61',
  #  'url': 'http://127.0.0.1:8000/f89e8597-7561-4170-bec3-9837b3f32d61/',
  #  'name': 'my entity',
  #  'parent': None,
  #  'children': [],
  #  'quantities': []}

  # Now delete the entity that was created above
  req.delete(response.json()["url"], headers=auth_header)

To alter an object, you can use the ``PATCH`` command. The following
example creates an object and then modifies its name::
  
  import requests as req

  server = "http://127.0.0.1:8000/"
  response = req.post(server + "api/entities/", data={
      "name": "my entity",
  })
  assert response.ok
  url = response.json()["url"]

  # This command changes "my entity" into "a better name"
  req.patch(url, data={"name": "a better name"})

You can also access an entity deeply nested in the tree using
the url http://server/tree/PATH. The ``PATH`` part is a nested
string of entities separated by ``/``, like for instance
``http://server/tree/instrument/electronic_board/board0``.
(Beware that InstrumentDB follows the HTTP protocol and returns
a HTTP 302 ``FOUND`` signal, so your library of choice might
need a further ``GET`` call to follow the alias. More advanced
libraries do this automatically: this is the case of the ``requests``
library we are using in these examples.)


Quantities
----------

You can query the list of quantities by issuing a ``GET`` command to
the url http://server/api/quantities/. To get information about one
entity, append the full UUID and a slash to it:
http://server/api/quantities/ede55e77-0dd1-483e-a307-e6e67759a450/.

To create a new quantity, you must issue a ``POST`` command with a
JSON record containing these keys:

- ``name``: a string
- ``format_spec``: the URL to a format specification object
- ``parent_entity``: the URL to an entity
- ``data_files``: a list of URLs for each data file. Passing ``[]`` is
  ok.

You can also access a quantity deeply nested in the tree of entities
using a technique similar to the one described above for entities.
If you are looking for a quantity named ``QUANTITY_NAME``, buried in
a deep branch of the tree of entities, you can use the url
http://server/tree/PATH/QUANTITY_NAME/, where the ``PATH`` part
is a nested string of entities separated by ``/``.
(Beware that InstrumentDB follows the HTTP protocol and returns
a HTTP 302 ``FOUND`` signal, so your library of choice might
need a further ``GET`` call to follow the alias. More advanced
libraries do this automatically: this is the case of the ``requests``
library we are using in these examples.)

As an example, suppose that the tree of entities is the following:

.. code-block:: text

   instrument
   |
   +-- electronic_board
   |
   +-- telescope
       |
       +--- mirror1
       |
       +--- mirror2


You can retrieve the entity for ``mirror2`` through the URL

.. code-block:: text

    http://server/tree/instrument/telescope/mirror2


Data files
----------

You can query the list of data files by issuing a ``GET`` command to
the url http://server/api/data_files/. To get information about one
entity, append the full UUID and a slash to it:
http://server/api/data_files/ede55e77-0dd1-483e-a307-e6e67759a450/.

To create a new data file, you must issue a ``POST`` command with a
JSON record containing these keys:

- ``name``: a name to be used when the data file is going to be
  downloaded locally into an actual file.
- ``upload_date``: the date and time when the file was created. If not
  provided, the current date will be used.
- ``file_data``: a file-like object containing the contents of the file.
- ``metadata``: a JSON structure containing custom metadata associated
  with the data file.
- ``quantity``: the URL to the quantity that owns this data file.
- ``spec_version``: a custom string specifying which version of the
  specification document (associated with ``quantity``) was used to
  produce this data file.
- ``dependencies``: a list of URLs to data files that have been used
  to produce this very data file (optional).
- ``plot_mime_type``: the MIME type of the plot associated with this
  data file (optional).
- ``plot_file``: a file-like object containing a visual representation
  of the data file.
- ``comment``: a string containing any comment (optional).
- ``release_tags``: a list of URLS to the releases that include this
  data file (optional).

Creating a ``POST`` command in Python with the
`requests <https://pypi.org/project/requests/>`_ library requires you
to send the JSON and (optionally) the two files containing the data
file itself and the plot. You can achieve this using both the ``data=``
and ``files=`` keywords when calling ``requests.post``, like in the
following example::

    import requests as req

    server_url = "http://127.0.0.1:8000"

    response = req.post(url=f"{server_url}/api/login",
        data={"username":"user1", "password": "passwd54321"}
    )
    assert response.ok
    auth_header = {"Authorization": "Token " + response.json()["token"]}

    response = req.post(
        url=f"{server_url}/api/data_files/",
        data={
            "name": "My data file",
            "quantity": f"{server_url}/api/quantities/4a0c5e12-da9c-4c7a-923e-810a19974444/",
            "spec_version": "1.0",
            "metadata": "{}",
            "plot_mime_type": "image/png",  # THIS IS MANDATORY IF YOU INCLUDE "plot_file" BELOW!
        },
        files={
            "file_data": open("/local_storage/spreadsheet.xlsx", "rb"),
            "plot_file": open("/local_storage/summary_plot.png", "rb"),
        },
        headers=auth_header,
    )

    assert response.ok

    uuid = response.json()["uuid"]
    print("Data file created, UUID is ", uuid)

It is *required* that you specify ``plot_mime_type`` if you plan to
pass ``plot_file`` like in the example above, because this will be used
to determine how to show the image when browsing the database through the
web interface.

If a data file is part of a release (see the section :ref:`Releases` below),
you can access it using the url http://server/releases/RELEASE/PATH/QUANTITY,
where ``RELEASE`` is the name of the release, ``PATH`` is the sequence of
of entity names separated by ``/``, and ``QUANTITY`` is the quantity which
hosts the data file. For instance, if the tree of entities is the following:

.. code-block:: text

   instrument
   |
   +-- electronic_board
   |
   +-- telescope
       |
       +--- mirror1
       |
       +--- mirror2

and the quantity you are looking for is the CAD for ``mirror2`` that
is stored under the quantity ``design_cad``, you can access the CAD
that was saved in release ``v2.03`` using the path

.. code-block:: text

    http://server/releases/v2.03/instrument/telescope/mirror2

.. _releases:
Releases
--------

You can query the list of releases by issuing a ``GET`` command to the
url http://server/api/releases/. To get information about one release,
append its name and a slash to it: http://server/api/releases/v0.28/.
Finally, to download the JSON file for one release (*without* attachments!)
append ``download/`` to its URL: http://server/api/releases/v0.28/download/.

To create a new release, you must issue a ``POST`` command with a
JSON record containing these keys:

- ``tag``: the name of the release. The only characters allowed here
  are letters, digits, the underscore and the dot.
- ``rel_date``: the date when the release was created. If not
  specified, the current date is used.
- ``comment``: a string containing any useful comment regarding this
  release (optional).
- ``data_files``: a list of URLs containing the data files.

To associate data files to releases, you can use one of the following
approaches:

1. Add data files to the release tag as soon as you create it;
2. Add data files to the release tag after having created the release;
3. Add releases to a data file.

Let's see each of the three approaches. The first one is the simplest::

  import requests as req

  server = "http://127.0.0.1:8000/"

  # Get authentication token (login)
  response = req.post(url=f"{server_url}/api/login",
      data={"username":"user1", "password": "passwd54321"}
  )
  auth_header = {"Authorization": "Token " + response.json()["token"]}

  # Name of the release we're going to create
  release_name = "v0.10"

  # These are the data files to be added to the release
  data_files = [
      "http://127.0.0.1:8000/api/data_files/021d0dfa-e54a-44ca-abc8-ac1d01ed4c50/",
      "http://127.0.0.1:8000/api/data_files/791a310e-f950-4370-bcf0-bc49622847c9/",
      "http://127.0.0.1:8000/api/data_files/34c11186-2ce2-4805-9114-91ed460c6a95/",
  ]
  # Create the release
  response = requests.post(
      server + "api/releases/", data={
          "tag": release_name,
          "comment": "dummy release",
          "data_files": data_files,
      },
      headers=auth_header,
  )

Let's now consider the case where you did not pass the ``data_files``
key in the POST command above. (For instance, you were still building
the list of data files.) Assuming that a release was already created,
you can use ``PATCH`` commands to modify the release object, as shown
in this snippet::

  # We are re-using the "req" object got in the snippet above through
  # the call to `requests.post`
  release_info = response.json()
  
  # This is the URL of the release we created
  url = response.json()["url"]
  
  # We are re-using "tag" and "comment" from the call to `request.post`
  # above, but we might change them as well in this call, as the HTTP
  # `patch` command overwrites everything.
  requests.patch(
      url,
      data={
          "tag": release_info["tag"],
          "comment": release_info["comment"],
          "data_files": data_files,
      },
      headers=auth_header,
  )
  
Alternatively, we can go through the opposite route and add the
release tag to every data file in the list ``data_files``. The
following snippet is equivalent to the code above::

  for cur_data_file_url in data_files:
      # Retrieve the current data file
      cur_data_file = req.get(cur_data_file_url, headers=auth_header).json()

      # Append the URL to the new release to the list of release tags
      cur_data_file["release_tags"].append(release_info["url"])

      # Modify the data file in the database
      req.patch(cur_data_file_url, data=cur_data_file, headers=auth_header)
