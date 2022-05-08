Credentials
===========

Youtube:
--------


**Enable APIs for your project**

Any application that calls Google APIs needs to enable those APIs in
the API Console. To enable the appropriate APIs for your project:

1. Open the `Library page <https://console.developers.google.com/apis/library>`_
    in the API Console.
2. Select the project associated with your application. Create a project if you
    do not have one already.
3. Use the Library page to find each API that your application will use.
    Click on each API and enable it for your project.

**Create authorization credentials**

Any application that uses OAuth 2.0 to access Google APIs must have
authorization credentials that identify the application to Google's
OAuth 2.0 server. The following steps explain how to create credentials
for your project. Your applications can then use the credentials to
access APIs that you have enabled for that project.

1. Open the `Credentials page <https://console.developers.google.com/apis/credentials/>`_.
    in the API Console.
2. Click Create credentials > OAuth client ID.
3. Complete the form. Set the application type to **other**.

.. image:: /_static/google.console.png

Download your ``client_secret.json`` and assuming the file is on your user
downloads directory run and follow the on screen instructions


.. code-block:: console

   $ pytuber setup youtube ~/Downloads/client_secret_foobar.json


Last.fm
-------

Apply for a last.fm `api key <https://www.last.fm/api/account/create>`_
write down your key **key** and run from terminal

.. code-block:: console

   $ pytuber setup lastfm --api-key abcdefghijklmnop
