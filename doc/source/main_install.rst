Installation
============

Requirements
------------

System requirements
~~~~~~~~~~~~~~~~~~~

* **Python**: 3.6 or later
* **mock**: RPM building tool
* **PyYAML**: Python YAML library
* **podman or docker**: Required only for container install type (optional)

Operating system support
~~~~~~~~~~~~~~~~~~~~~~~~

rpm-build-assist is tested on:

* Fedora (current and previous two releases)
* RHEL/CentOS 8 and later
* Any Linux distribution with mock support

Permissions
~~~~~~~~~~~

You must be a member of the ``mock`` group to run mock builds. After
installation, add yourself to the group:

.. code-block:: bash

   sudo usermod -a -G mock $USER

**Important**: You must log out and log back in for the group membership to
take effect.

Installing rpm-build-assist
----------------------------

From source
~~~~~~~~~~~

Clone the repository and make the script executable:

.. code-block:: bash

   git clone https://codeberg.org/orb-project/rpm-build-assist.git
   cd rpm-build-assist
   chmod +x rpm-build-assist

The tool is a single Python script with no installation required. You can:

* Run it directly from the cloned directory
* Copy it to a directory in your PATH (e.g., ``~/.local/bin/``)
* Create a symlink in your PATH

From a package (future)
~~~~~~~~~~~~~~~~~~~~~~~

RPM and DEB packages may be provided in the future.

Installing dependencies
-----------------------

Fedora/RHEL/CentOS
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install mock and PyYAML
   sudo dnf install mock python3-pyyaml

   # Optional: Install container runtime for container builds
   sudo dnf install podman

   # Or use docker instead
   sudo dnf install docker

Debian/Ubuntu
~~~~~~~~~~~~~

.. code-block:: bash

   # Install mock and PyYAML
   sudo apt-get install mock python3-yaml

   # Optional: Install podman
   sudo apt-get install podman

Verifying installation
----------------------

Test that mock is installed and you have permission to use it:

.. code-block:: bash

   # This should NOT show a permission error
   mock --version

If you see a permission error, ensure you're in the mock group and have
logged out and back in.

Test rpm-build-assist:

.. code-block:: bash

   ./rpm-build-assist --help

You should see the help message with usage information.

Optional: Container runtime
----------------------------

If you plan to use the ``container`` install type, you need either podman
or docker installed.

Verify container runtime:

.. code-block:: bash

   # For podman
   podman --version

   # For docker
   docker --version

rpm-build-assist will automatically detect which one is available.

Setting up mock
---------------

Mock configuration files
~~~~~~~~~~~~~~~~~~~~~~~~

Mock configurations are stored in ``/etc/mock/``. View available
configurations:

.. code-block:: bash

   ls /etc/mock/*.cfg

Common configurations include:

* ``fedora-39-x86_64.cfg``
* ``fedora-40-x86_64.cfg``
* ``epel-9-x86_64.cfg``
* ``centos-stream-9-x86_64.cfg``

You'll specify one of these (without the ``.cfg`` extension) as the ``base``
in your build-assist.yaml configuration.

Mock plugins
~~~~~~~~~~~~

Ensure the mock SCM plugin is available. This should be installed by default
with modern mock versions:

.. code-block:: bash

   # Check for SCM plugin
   rpm -ql mock | grep scm

Network configuration
~~~~~~~~~~~~~~~~~~~~~

Mock builds run in isolated environments. Ensure your system's network is
configured correctly if your builds need to access package repositories.

Next steps
----------

* Read the :doc:`tutorial/first_build` to create your first build
* Review the :doc:`format/yaml_format` to understand configuration options
* Check out example configurations in the repository's ``examples/`` directory

Troubleshooting installation
-----------------------------

Permission denied when running mock
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``ERROR: You must be root or a member of the mock group``

**Solution**:

1. Add yourself to the mock group:

   .. code-block:: bash

      sudo usermod -a -G mock $USER

2. Log out completely and log back in
3. Verify group membership:

   .. code-block:: bash

      groups | grep mock

Python version too old
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``SyntaxError`` or version-related errors

**Solution**: Ensure you're using Python 3.6 or later:

.. code-block:: bash

   python3 --version

Mock configuration not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``ERROR: Could not find configuration file``

**Solution**: Install mock configuration files:

.. code-block:: bash

   sudo dnf install mock-core-configs

   # Or on Debian/Ubuntu
   sudo apt-get install mock-core-configs
