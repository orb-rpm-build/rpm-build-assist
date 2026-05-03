.. _tutorial_software_collections:

Software Collections
====================

This tutorial explains how to build software collections and package
collections using rpm-build-assist.

What are software collections?
-------------------------------

Software collections allow you to install software into a custom prefix
(typically ``/opt/collection-name``) instead of the standard ``/usr``. This
enables:

* Multiple versions of the same software installed simultaneously
* Isolated environments for specific applications
* Custom software stacks without conflicting with system packages

What are package collections?
------------------------------

Package collections are similar to software collections but use RPATHs to
handle library dependencies automatically. They don't require environment
variables or wrapper scripts to run.

When to use each
----------------

**Software collections** when:
  * You need environment modules or wrapper scripts
  * Following traditional SCL conventions
  * Need full environment isolation

**Package collections** when:
  * You want binaries that "just work" without environment setup
  * Prefer RPATH-based library resolution
  * Building self-contained application stacks

Software Collection Tutorial
-----------------------------

Step 1: Basic software collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a ``build-assist.yaml`` for a Python 3.11 software collection:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://internal.example.com/scl/
       packages:
         - python311:main
         - python311-pip:main
         - python311-setuptools:main

   install:
     type: software-collection
     collection: python311
     packages:
       - python311
       - python311-pip
       - python311-setuptools

What this does
^^^^^^^^^^^^^^

When you build with ``type: software-collection``, rpm-build-assist
configures RPM macros to install everything to ``/opt/python311``:

* ``_prefix`` → ``/opt/python311``
* ``_bindir`` → ``/opt/python311/bin``
* ``_libdir`` → ``/opt/python311/lib64``
* ``_datadir`` → ``/opt/python311/share``

Step 2: Build the collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist -v

Your packages will be built with the custom prefix.

Step 3: Using the software collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the RPMs on a system, you need to set up the environment:

.. code-block:: bash

   # Add to PATH
   export PATH=/opt/python311/bin:$PATH

   # Add to LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=/opt/python311/lib64:$LD_LIBRARY_PATH

   # Now you can use python3.11
   python3.11 --version

Typically, software collections include wrapper scripts or environment
modules to set these up automatically.

Package Collection Tutorial
----------------------------

Step 1: Basic package collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a ``build-assist.yaml`` for a self-contained application stack:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://internal.example.com/apps/
       packages:
         - myapp:main
         - myapp-libs:main
         - myapp-tools:main

   install:
     type: package-collection
     collection: myapp-stack
     packages:
       - myapp
       - myapp-libs
       - myapp-tools

What makes this different
^^^^^^^^^^^^^^^^^^^^^^^^^^

With ``type: package-collection``, rpm-build-assist:

1. Sets the same prefix as software collections (``/opt/myapp-stack``)
2. Adds RPATH configuration to compiled binaries
3. Sets ``LD_RUN_PATH`` during build to include ``$ORIGIN/../$LIB``

The ``$ORIGIN`` token
^^^^^^^^^^^^^^^^^^^^^

``$ORIGIN`` is a special token that expands at runtime to the directory
containing the binary. This enables relative library paths.

``$LIB`` expands to ``lib`` or ``lib64`` depending on the architecture.

Step 2: Build the package collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist -v

Step 3: Using the package collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the RPMs, binaries work without environment setup:

.. code-block:: bash

   # No PATH or LD_LIBRARY_PATH needed!
   /opt/myapp-stack/bin/myapp --version

The binary finds its libraries automatically via RPATH.

How RPATH works
^^^^^^^^^^^^^^^

When you run ``/opt/myapp-stack/bin/myapp``, the dynamic linker searches for
libraries in:

1. RPATH embedded in the binary (``$ORIGIN/../$LIB``)

   * ``$ORIGIN`` = ``/opt/myapp-stack/bin``
   * ``$ORIGIN/..`` = ``/opt/myapp-stack``
   * ``$ORIGIN/../$LIB`` = ``/opt/myapp-stack/lib64``

2. Absolute path in RPATH (``/opt/myapp-stack/lib64``)

This works regardless of your PATH or LD_LIBRARY_PATH.

Advanced: Flatpak prefix
------------------------

For building packages for flatpak, use:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:main

   install:
     type: flatpak
     packages:
       - myapp

This configures packages to install to ``/app`` instead of ``/usr``, which is
the standard prefix for flatpak runtimes.

Comparison table
----------------

.. list-table:: Installation Type Comparison
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - Standard
     - Flatpak
     - Software Collection
     - Package Collection
   * - Prefix
     - ``/usr``
     - ``/app``
     - ``/opt/{name}``
     - ``/opt/{name}``
   * - RPATH
     - No
     - No
     - No
     - Yes (``$ORIGIN``)
   * - Needs env setup
     - No
     - No
     - Yes
     - No
   * - Multiple versions
     - No
     - N/A
     - Yes
     - Yes

Spec file requirements
----------------------

For software collections
~~~~~~~~~~~~~~~~~~~~~~~~

Your spec files must respect RPM macros. Use:

.. code-block:: spec

   %configure --prefix=%{_prefix}
   make install DESTDIR=%{buildroot}

Not:

.. code-block:: spec

   ./configure --prefix=/usr  # Hard-coded prefix!

For package collections
~~~~~~~~~~~~~~~~~~~~~~~

Same as software collections, but also ensure your build system respects
compiler flags. Most autotools/cmake projects do this automatically.

If you're using custom makefiles, ensure ``LDFLAGS`` is respected:

.. code-block:: makefile

   myapp: myapp.o
       $(CC) $(LDFLAGS) -o myapp myapp.o -lmylib

The ``LDFLAGS`` will include the RPATH configuration.

Testing collections
-------------------

Verify the prefix
~~~~~~~~~~~~~~~~~

After building, check that files are installed to the correct prefix:

.. code-block:: bash

   rpm -qpl localrepo/myapp-*.rpm | head

You should see paths like ``/opt/myapp-stack/bin/...``

Verify RPATH (package collections only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the package and check the RPATH:

.. code-block:: bash

   # Install the RPM
   sudo dnf install localrepo/myapp-*.rpm

   # Check RPATH
   readelf -d /opt/myapp-stack/bin/myapp | grep RPATH

You should see:

.. code-block:: text

   0x000000000000000f (RPATH)    Library rpath: [$ORIGIN/../$LIB]

Test the binary
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Should work without environment setup (package collections)
   /opt/myapp-stack/bin/myapp --version

   # Check which libraries it loads
   ldd /opt/myapp-stack/bin/myapp

Common issues
-------------

Binary can't find libraries (software collections)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``error while loading shared libraries: libmyapp.so.1``

**Solution**: Set ``LD_LIBRARY_PATH``:

.. code-block:: bash

   export LD_LIBRARY_PATH=/opt/myapp-stack/lib64:$LD_LIBRARY_PATH

Or use a package collection instead, which handles this automatically.

RPATH not set (package collections)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``readelf`` shows no RPATH

**Causes**:

1. Build system doesn't respect ``LDFLAGS``
2. Binary is a script, not a compiled binary (scripts don't have RPATH)
3. Static linking (static binaries don't need RPATH)

**Solution**: Ensure your build system uses ``LDFLAGS`` when linking.

Files installed to /usr instead of /opt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: RPM installs to ``/usr`` instead of ``/opt/collection``

**Cause**: Spec file hard-codes ``--prefix=/usr``

**Solution**: Update the spec file to use ``%{_prefix}``

Best practices
--------------

Name collections consistently
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use descriptive, versioned names:

* ``python311`` not ``python``
* ``nodejs20`` not ``node``
* ``myapp-v2`` not ``myapp``

Document environment requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For software collections, document the required environment setup in your
package's README.

Provide wrapper scripts
~~~~~~~~~~~~~~~~~~~~~~~

Software collections often include wrapper scripts:

.. code-block:: bash

   #!/bin/bash
   # /usr/bin/python311

   export LD_LIBRARY_PATH=/opt/python311/lib64:$LD_LIBRARY_PATH
   exec /opt/python311/bin/python3.11 "$@"

Consider package collections for simpler UX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your users don't need environment isolation, package collections provide
a better experience (binaries "just work").

Next steps
----------

* Learn about :doc:`container_builds` to containerize collections
* See :doc:`../format/install_section` for all install type options
* Read :doc:`../howto/custom_macros` for advanced macro configuration
