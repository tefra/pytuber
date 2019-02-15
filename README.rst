pytuber
=======


.. image:: https://travis-ci.org/tefra/pytuber.svg?branch=master
    :target: https://travis-ci.org/tefra/pytuber

.. image:: https://readthedocs.org/projects/pytuber/badge
    :target: https://pytuber.readthedocs.io/en/latest

.. image:: https://codecov.io/gh/tefra/pytuber/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/tefra/pytuber

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. image:: https://img.shields.io/github/languages/top/tefra/pytuber.svg
    :target: https://pytuber.readthedocs.io/


.. image:: https://img.shields.io/pypi/pyversions/pytuber.svg
    :target: https://pypi.org/pypi/pytuber/

.. image:: https://img.shields.io/pypi/v/pytuber.svg
    :target: https://pypi.org/pypi/pytuber/

----

.. image:: https://github.com/tefra/pytuber/raw/master/docs/_static/demo.gif
    :align: center

----

**pytuber** is a cli tool to manage your music **playlists** on youtube.
  - Generate playlists from `Last.fm <https://www.last.fm>`_ or
  - Import from file formats: XSPF, JSPF, M3U
  - Create with a simple copy paste in a text editor
  - Search and match tracks to Youtube videos
  - Sync pytuber playlists (fetch/push)
  - Update youtube playlist items (add/remove)
  - Keep track of youtube api quota usage


Install & Setup
~~~~~~~~~~~~~~~

.. code-block:: console

    $ pip install pytuber
    $ pytuber setup autocomplete  # Enable autocomplete


Read how to setup youtube `authentication <https://pytuber.readthedocs.io/en/latest/credentials.html>`_

Start creating youtube playlists ✨✨


Youtube API Quota
~~~~~~~~~~~~~~~~~

Youtube api has a daily api `quota <https://developers.google.com/youtube/v3/getting-started#quota>`_ limit which resets at midnight Pacific Time (PT).

pytuber includes a quota calculator

.. code-block:: console

    $ pytuber quota

Additionally to the api quota limit Youtube limits the amount of how many playlists you can create per day to only **10**.

In case you reach that number, you can push a new playlist manually.
  - Create a playlist with `pytuber add` command
  - View the playlist by using this command `pytuber show xxxx --mime`
  - This mime string is base64 signature used by pytuber internally to link local to youtube playlists
  - Add a youtube playlists manually from the web site and add the mime signature at the bottom of the playlist description
  - Fetch the new playlist info `pytuber fetch youtube --playlists`

Afterwards you will be aple to push tracks like normally.
