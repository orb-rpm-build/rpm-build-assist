Custom RPM Macros
=================

.. note::

   This feature is partially implemented. The install section configures
   macros automatically. Custom macro support for arbitrary use cases is
   planned for a future version.

Current macro support
---------------------

rpm-build-assist currently sets RPM macros automatically based on the install
type:

* ``flatpak``: Sets prefix to ``/app``
* ``software-collection``: Sets prefix to ``/opt/{collection}``
* ``package-collection``: Sets prefix to ``/opt/{collection}`` with RPATH

See :doc:`../reference/install_types` for details.

Workarounds for custom macros
------------------------------

Until custom macro support is added, you can:

1. Modify spec files
~~~~~~~~~~~~~~~~~~~~

Add macro definitions in your spec file:

.. code-block:: spec

   %global custom_prefix /opt/myapp
   %global custom_flag --enable-feature

   Name: myapp
   ...

2. Use ~/.rpmmacros
~~~~~~~~~~~~~~~~~~~

Define macros in ``~/.rpmmacros`` (affects all builds):

.. code-block:: text

   %custom_prefix /opt/myapp
   %custom_flag --enable-feature

3. Pass to mock
~~~~~~~~~~~~~~~

Not currently supported directly, but planned for future versions.

Planned feature
---------------

Future versions will support custom macros in the YAML:

.. code-block:: yaml

   base: fedora-39-x86_64

   macros:
     _custom_prefix: /opt/myapp
     _enable_feature: 1
     version_suffix: alpha1

   build:
     # Uses custom macros
     - url: https://github.com/myorg/
       packages:
         - myapp:main

Custom macro support is planned for a future version.

See also
--------

* :doc:`../reference/install_types` - Automatic macro configuration
* :doc:`../tutorial/software_collections` - Using install types
* RPM macro documentation: ``man rpm`` and ``rpm --showrc``
