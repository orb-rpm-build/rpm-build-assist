Command-Line Reference
======================

Synopsis
--------

.. code-block:: text

   rpm-build-assist [-h] [-c FILE] [-v] [--localrepo PATH]

Description
-----------

``rpm-build-assist`` is a tool for building RPM packages using mock with
SCM integration. It reads a YAML configuration file and builds the specified
packages in order, managing dependencies through a local repository.

Options
-------

.. program:: rpm-build-assist

.. option:: -h, --help

   Show help message and exit

.. option:: -c FILE, --config FILE

   Path to YAML configuration file

   Default: ``build-assist.yaml``

   The configuration file must be valid YAML and conform to the rpm-build-assist
   schema. See :doc:`../format/yaml_format` for details.

.. option:: -v, --verbose

   Enable verbose output

   Shows detailed information about:

   * Configuration loading
   * Mock commands being executed
   * Build progress
   * File operations

   Useful for debugging configuration issues or build failures.

.. option:: --localrepo PATH

   Path to local repository directory

   Default: Value from YAML ``localrepo`` field, or a temporary directory

   The local repository stores built RPMs and enables dependency resolution
   between packages. If the directory doesn't exist, it will be created.

   Use a persistent directory (not /tmp) to preserve builds between runs.

Examples
--------

Basic usage
~~~~~~~~~~~

Use default configuration file:

.. code-block:: bash

   ./rpm-build-assist

Specify configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist -c my-config.yaml

Enable verbose output
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist -v

Use persistent local repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist --localrepo ~/rpm-builds/localrepo

Combine options
~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist --verbose --config production.yaml --localrepo /var/cache/rpms

Exit status
-----------

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Code
     - Meaning
   * - 0
     - Success
   * - 1
     - Configuration error, build error, or other failure

Environment
-----------

rpm-build-assist respects standard environment variables:

**MOCK_CONFIG**
  If set and no ``-c`` option is given, uses this as the configuration file path

**NO_COLOR**
  If set to any value, disables colored output (future feature)

Files
-----

**build-assist.yaml**
  Default configuration file in current directory

**/etc/mock/\*.cfg**
  Mock configuration files

**~/.rpmmacros**
  RPM macro definitions (may affect builds)

**/var/lib/mock/**
  Mock build roots and results

Dependencies
------------

rpm-build-assist requires:

* Python 3.6 or later
* mock
* PyYAML
* podman or docker (for container builds only)

Limitations
-----------

* Must be run as a user in the ``mock`` group
* Cannot run builds in parallel (builds are sequential)
* Limited to mock-supported architectures
* Requires network access for source checkout (can't work offline)

See also
--------

* :doc:`../main_using` - User guide
* :doc:`../format/yaml_format` - Configuration format
* :doc:`../howto/troubleshooting` - Common issues

Bugs
----

Report bugs on Codeberg: https://codeberg.org/orb-project/rpm-build-assist/issues
