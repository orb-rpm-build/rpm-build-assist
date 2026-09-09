Command-Line Reference
======================

Synopsis
--------

.. code-block:: text

   rpm-build-assist [-h] [-c FILE] [-v] [-f] [--localrepo PATH]

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

.. option:: -f, --force

   Rebuild even when the build cache indicates nothing has changed.

   By default, before building a package rpm-build-assist resolves its branch
   to a commit with ``git ls-remote`` and skips the entire checkout and build
   when the commit, target config, and mock macros/repositories all match the
   last successful build. ``--force`` ignores that cache and rebuilds.

   See `Build cache`_ for details.

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

Force a rebuild
~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist --localrepo ~/rpm-builds/localrepo --force

Combine options
~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist --verbose --config production.yaml --localrepo /var/cache/rpms

Build cache
-----------

To avoid redoing work, rpm-build-assist skips a package when nothing that
affects its output has changed since the last successful build.

Before building, it resolves the package's branch to a commit with a single
``git ls-remote`` (no clone). It then compares a key derived from that commit,
the target ``base`` config, and the mock macros and additional repositories
against the last recorded build. On a match, the checkout, src.rpm build, and
chain build are all skipped.

Where the record lives
~~~~~~~~~~~~~~~~~~~~~~~

Each successful build writes a human-readable ``build-assist.result`` file into
that package's result directory in the local repository. It is then linked into
a ``build-assist.result-cache`` directory beside your configuration file, with
one symlink per package::

   build-assist.yaml
   build-assist.result-cache/
       demo -> /path/to/localrepo/results/fedora-44-x86_64/demo-1.0-1.fc44/build-assist.result

Both locations are ordinary, visible files you can inspect or delete. To
invalidate a cached build, remove **either** the symlink in
``build-assist.result-cache`` **or** the package's result directory (a removed
result directory leaves the symlink dangling, which counts as no cache).

Notes:

* The cache is only useful with a persistent :option:`--localrepo`; a temporary
  one starts empty on every run.
* If a branch can't be resolved to a commit (for example a raw commit hash used
  as a ``git`` ref), the build is not skipped.
* The record notes that a build succeeded; it does not re-verify every RPM. If
  you remove RPMs by hand, remove the matching cache entry or use
  :option:`--force` to rebuild.
* If your configuration lives in a git repository, add
  ``build-assist.result-cache/`` to ``.gitignore``.

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
