Using rpm-build-assist
======================

This section provides an overview of using rpm-build-assist for common tasks.

Basic usage
-----------

The basic workflow is:

1. Create a YAML configuration file describing your builds
2. Run ``rpm-build-assist`` to execute the builds
3. Find built RPMs in the local repository
4. Optionally deploy to containers or other targets

Command-line interface
----------------------

Basic invocation
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use default configuration file (build-assist.yaml)
   ./rpm-build-assist

   # Specify a custom configuration file
   ./rpm-build-assist -c my-config.yaml

Command-line options
~~~~~~~~~~~~~~~~~~~~

.. program:: rpm-build-assist

.. option:: -c FILE, --config FILE

   Path to YAML configuration file. Default: ``build-assist.yaml``

.. option:: -v, --verbose

   Enable verbose output for detailed logging and debugging

.. option:: --localrepo PATH

   Path to local repository directory. If not specified, uses the
   ``localrepo`` setting from the YAML file, or creates a temporary
   directory.

Examples
^^^^^^^^

.. code-block:: bash

   # Enable verbose output
   ./rpm-build-assist -v

   # Use a persistent local repository
   ./rpm-build-assist --localrepo /path/to/repo

   # Combine options
   ./rpm-build-assist --verbose --config custom.yaml --localrepo ~/rpms

Configuration file
------------------

The configuration file is a YAML document with three main sections:

.. code-block:: yaml

   base: <mock-configuration>

   build:
     - <build-sources>

   install:  # optional
     <installation-target>

Minimal configuration
~~~~~~~~~~~~~~~~~~~~~

A minimal configuration requires only ``base`` and ``build``:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide

This builds the ``htop`` package from Fedora's dist-git.

See :doc:`format/yaml_format` for complete format documentation.

Build process
-------------

When you run rpm-build-assist, it performs the following steps:

1. **Load configuration**

   Reads and validates the YAML configuration file.

2. **Process install section**

   If an install section is present, determines what RPM macros need to be
   set (e.g., for flatpak or software collections).

3. **Setup local repository**

   Creates or uses an existing directory to store built RPMs. This repository
   enables dependency resolution between packages.

4. **Build packages**

   For each package:

   * Constructs the repository URL
   * Invokes mock with SCM options
   * Uses ``--chain`` for dependency resolution
   * Stores built RPMs in the local repository

5. **Create installation target**

   If an install section is specified, creates the target:

   * **container**: Builds a container image
   * **flatpak/software-collection**: Packages are built with appropriate macros
   * Other types may be implemented in the future

Build artifacts
---------------

Local repository
~~~~~~~~~~~~~~~~

Built RPMs are stored in the local repository directory. The structure is:

.. code-block:: text

   localrepo/
   ├── package1-version.rpm
   ├── package2-version.rpm
   ├── package3-version.rpm
   └── repodata/
       └── (repository metadata)

You can use this as a standard DNF/YUM repository.

Container images
~~~~~~~~~~~~~~~~

When using the ``container`` install type, the resulting container image is
available in your local container storage:

.. code-block:: bash

   # List images
   podman images
   # or
   docker images

   # Run the container
   podman run -it <your-tag>

Mock results
~~~~~~~~~~~~

Mock build results are stored in ``/var/lib/mock/<config>/result/`` by
default. This includes:

* Build logs
* Source and binary RPMs
* Mock build state

Common workflows
----------------

Building a single package
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://github.com/myorg/
       packages:
         - myapp:main

Building multiple packages with dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://github.com/myorg/
       packages:
         - mylib:v1.0    # Built first
         - myapp:main    # Can depend on mylib

Packages are built in the order listed. The ``--chain`` mode ensures that
later packages can find earlier ones in the local repository.

Creating a container image
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://github.com/myorg/
       packages:
         - myapp:v2.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:v2.0
     packages:
       - myapp

See :doc:`tutorial/container_builds` for more details.

Building for flatpak
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://github.com/myorg/
       packages:
         - myapp:main

   install:
     type: flatpak
     packages:
       - myapp

This automatically configures RPM to install to ``/app`` instead of ``/usr``.

Reusing a local repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a persistent local repository to speed up rebuilds:

.. code-block:: bash

   # First build
   ./rpm-build-assist --localrepo ~/my-repo

   # Later builds reuse the repository
   ./rpm-build-assist --localrepo ~/my-repo

Or specify in the YAML:

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: ~/my-repo

   build:
     # ...

Tips and best practices
-----------------------

Start with verbose mode
~~~~~~~~~~~~~~~~~~~~~~~

When first setting up your builds, use ``-v`` to see what's happening:

.. code-block:: bash

   ./rpm-build-assist -v

This shows mock commands, build progress, and helps diagnose issues.

Order packages by dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List packages in dependency order in your YAML file. Libraries and
dependencies should come before packages that use them.

Use persistent repositories for development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During development, use a persistent local repository to avoid rebuilding
unchanged packages:

.. code-block:: bash

   ./rpm-build-assist --localrepo ~/dev/localrepo

Test with simple packages first
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before building complex dependency chains, test with a single simple package
to ensure your configuration is correct.

Check mock logs for build failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a build fails, check the mock logs in
``/var/lib/mock/<config>/result/build.log`` for details.

Next steps
----------

* Follow the :doc:`tutorial/first_build` for a hands-on introduction
* Learn about :doc:`format/yaml_format` options
* Explore :doc:`howto/mixed_sources` for complex builds
* See :doc:`howto/troubleshooting` for common issues
