.. _tutorial_first_build:

Your First Build
================

This tutorial will walk you through creating your first rpm-build-assist
configuration and building a simple package.

Prerequisites
-------------

Before starting, ensure you have:

* Installed rpm-build-assist (see :doc:`../main_install`)
* Added yourself to the ``mock`` group
* Logged out and back in to activate group membership

Step 1: Create a configuration file
------------------------------------

Create a file named ``build-assist.yaml`` with the following content:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide

This configuration:

* Uses the Fedora 39 x86_64 mock configuration
* Fetches the ``htop`` package from Fedora's dist-git
* Checks out the ``rawhide`` branch

Understanding the configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**base**
  The mock configuration to use. Available configurations are in
  ``/etc/mock/``. Use the filename without the ``.cfg`` extension.

**build**
  A list of source repositories and packages to build.

**type**
  The SCM (Source Code Management) type. ``dist-git`` is the default and is
  used by Fedora, CentOS, and RHEL.

**url**
  The base URL for repositories. Package names are appended to this URL.

**packages**
  A list of packages to build. Format is ``package-name:branch``. If the
  branch is omitted, ``main`` is used.

Step 2: Run the build
----------------------

Execute rpm-build-assist:

.. code-block:: bash

   ./rpm-build-assist -v

The ``-v`` flag enables verbose output so you can see what's happening.

What happens during the build
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll see output similar to:

.. code-block:: text

   INFO: Using mock config: fedora-39-x86_64
   INFO: Local repository: /tmp/tmp_xyz123
   INFO: Building package: htop:rawhide
   INFO: Running mock with SCM options...
   INFO: Build completed: htop
   INFO: Built packages stored in: /tmp/tmp_xyz123

rpm-build-assist will:

1. Create a temporary local repository
2. Configure mock to use dist-git SCM
3. Clone the htop repository
4. Check out the rawhide branch
5. Build the RPM using mock
6. Store the built RPM in the local repository

Step 3: Find your built packages
---------------------------------

The built RPMs are in the temporary local repository. The exact path is shown
in the output. List the contents:

.. code-block:: bash

   ls /tmp/tmp_xyz123/

You should see:

* ``htop-<version>.rpm`` - The built package
* ``htop-<version>.src.rpm`` - The source RPM
* ``repodata/`` - Repository metadata

Installing the package
~~~~~~~~~~~~~~~~~~~~~~

You can install the built package:

.. code-block:: bash

   sudo dnf install /tmp/tmp_xyz123/htop-*.rpm

Or test it without installing:

.. code-block:: bash

   rpm -qpl /tmp/tmp_xyz123/htop-*.rpm

Step 4: Use a persistent repository
------------------------------------

By default, rpm-build-assist uses a temporary directory that's deleted when
your system is rebooted. For development, it's better to use a persistent
directory.

Modify your ``build-assist.yaml``:

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: ./localrepo

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide

Now run the build again:

.. code-block:: bash

   ./rpm-build-assist -v

The built RPMs will be in ``./localrepo/`` in your current directory. This
directory persists between builds.

Benefits of persistent repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Packages remain available after reboot
* Faster rebuilds when you need to build again
* Easy to share or backup your built packages
* Can be used as a DNF repository

Step 5: Build multiple packages
--------------------------------

Let's build two packages. Modify your configuration:

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: ./localrepo

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide
         - tmux:rawhide

Run the build:

.. code-block:: bash

   ./rpm-build-assist -v

Both packages will be built and stored in ``./localrepo/``.

Understanding build order
~~~~~~~~~~~~~~~~~~~~~~~~~

Packages are built in the order listed. If ``tmux`` depended on ``htop``
(it doesn't in this example), listing ``htop`` first ensures it's available
when building ``tmux``.

The ``--chain`` mode in mock allows later packages to use earlier packages
from the local repository.

Step 6: Build from a git repository
------------------------------------

You can also build from regular git repositories (not just dist-git). Here's
an example:

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: ./localrepo

   build:
     - type: git
       url: https://github.com/yourusername/
       packages:
         - mypackage:main

This assumes:

* The repository is at ``https://github.com/yourusername/mypackage``
* The repository contains a ``.spec`` file
* The branch is ``main``

Requirements for git repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``type: git``, your repository must contain:

* A valid RPM ``.spec`` file
* Source files (or the spec must download them)

The ``.spec`` file should be in the root directory and match the package
name (e.g., ``mypackage.spec``).

Common issues
-------------

Permission denied
~~~~~~~~~~~~~~~~~

If you see:

.. code-block:: text

   ERROR: You must be root or a member of the mock group

You need to:

1. Add yourself to the mock group: ``sudo usermod -a -G mock $USER``
2. Log out and log back in
3. Verify: ``groups | grep mock``

Mock configuration not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you see:

.. code-block:: text

   ERROR: Could not find configuration file

The ``base`` in your YAML doesn't match a file in ``/etc/mock/``. Check
available configurations:

.. code-block:: bash

   ls /etc/mock/*.cfg

Build failed
~~~~~~~~~~~~

If a package fails to build:

1. Check the mock logs: ``/var/lib/mock/fedora-39-x86_64/result/build.log``
2. Look for compilation errors or missing dependencies
3. The issue may be with the package itself, not rpm-build-assist

Next steps
----------

Now that you've completed your first build, you can:

* Learn about :doc:`container_builds` to create container images
* Explore :doc:`software_collections` for custom installation prefixes
* Read the :doc:`../format/yaml_format` for all configuration options
* See :doc:`../howto/mixed_sources` for building from multiple repositories
