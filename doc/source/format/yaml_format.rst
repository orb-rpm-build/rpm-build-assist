.. _format_yaml:

YAML Configuration Format
==========================

The rpm-build-assist configuration file is a YAML document that describes
what to build and how to build it.

Overview
--------

A complete configuration has three top-level sections:

.. code-block:: yaml

   base: <mock-configuration>

   localrepo: <path>  # Optional

   addrepo: <url-or-list>  # Optional

   build:
     - <source-definition>
     - <source-definition>
     ...

   install:  # Optional
     type: <install-type>
     <install-specific-fields>

Only ``base`` and ``build`` are required.

Top-level fields
----------------

base
~~~~

**Required**: Yes

**Type**: String

**Description**: The mock configuration to use for builds.

Available configurations are in ``/etc/mock/``. Use the filename without the
``.cfg`` extension.

**Example**:

.. code-block:: yaml

   base: fedora-39-x86_64

**Common values**:

* ``fedora-39-x86_64``
* ``fedora-40-x86_64``
* ``epel-9-x86_64``
* ``centos-stream-9-x86_64``

localrepo
~~~~~~~~~

**Required**: No

**Type**: String (path)

**Description**: Path to a directory to use as the local repository for built
RPMs.

If not specified, a temporary directory will be created. The command-line
option ``--localrepo`` takes precedence over this setting.

**Example**:

.. code-block:: yaml

   localrepo: /home/user/rpm-builds/localrepo

**Use cases**:

* Preserve built RPMs between runs
* Share a repository across multiple build configurations
* Debug build issues by inspecting repository contents

addrepo
~~~~~~~

**Required**: No

**Type**: String or list of strings

**Description**: Additional repository URLs to make available during builds.

These repositories are passed to mock with the ``--addrepo`` flag, making
packages available for build-time dependencies.

**Example (single repository)**:

.. code-block:: yaml

   addrepo: https://example.com/custom-repo/fedora-39-x86_64/

**Example (multiple repositories)**:

.. code-block:: yaml

   addrepo:
     - https://example.com/repo1/fedora-39-x86_64/
     - https://example.com/repo2/fedora-39-x86_64/
     - https://download.copr.fedorainfracloud.org/results/@company/libs/

build
~~~~~

**Required**: Yes

**Type**: List of source definitions

**Description**: Defines what packages to build and where to fetch them from.

See :doc:`build_section` for detailed documentation.

**Example**:

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide
         - tmux:f39

     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:main

install
~~~~~~~

**Required**: No

**Type**: Object

**Description**: Defines how built packages should be installed or packaged.

If specified, this section affects the build process by setting RPM macros
and may create additional artifacts (like container images).

See :doc:`install_section` for detailed documentation.

**Example**:

.. code-block:: yaml

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:latest
     packages:
       - myapp

File format
-----------

Character encoding
~~~~~~~~~~~~~~~~~~

Configuration files must be UTF-8 encoded.

YAML version
~~~~~~~~~~~~

rpm-build-assist uses YAML 1.1 as implemented by PyYAML.

Comments
~~~~~~~~

YAML comments start with ``#``:

.. code-block:: yaml

   # This is a comment
   base: fedora-39-x86_64  # Inline comment

Strings
~~~~~~~

Strings can be unquoted, single-quoted, or double-quoted:

.. code-block:: yaml

   # All equivalent
   collection: myapp
   collection: 'myapp'
   collection: "myapp"

Use quotes when the string contains special characters:

.. code-block:: yaml

   tag: "myapp:latest"  # Colon requires quotes

Multiline strings
~~~~~~~~~~~~~~~~~

Use ``|`` for literal blocks:

.. code-block:: yaml

   description: |
     This is a multiline
     description of my build
     configuration.

Lists
~~~~~

Lists can be written in two ways:

.. code-block:: yaml

   # Flow style
   packages: [htop, tmux, vim]

   # Block style (preferred)
   packages:
     - htop
     - tmux
     - vim

Objects/dictionaries
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Flow style
   install: {type: container, tag: myapp:latest}

   # Block style (preferred)
   install:
     type: container
     tag: myapp:latest

Anchors and aliases
~~~~~~~~~~~~~~~~~~~

YAML anchors and aliases are supported:

.. code-block:: yaml

   common: &common_packages
     - bash
     - coreutils

   build:
     - url: https://example.com/
       packages:
         - myapp:main
         - *common_packages  # Reference the anchor

Best practices
--------------

Use descriptive names
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good
   localrepo: ./myproject-rpms

   # Less clear
   localrepo: ./lr

Order packages logically
~~~~~~~~~~~~~~~~~~~~~~~~

List packages in dependency order:

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         - mylib:v1.0      # Library first
         - myapp:v1.0      # App that depends on mylib

Group related sources
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     # Official Fedora packages
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide
         - postgresql:f39

     # Custom packages
     - type: git
       url: https://github.com/myorg/
       packages:
         - webapp:v2.0

Use comments for clarity
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         # Core application
         - myapp:v2.0

         # Optional plugins
         - myapp-plugin-auth:v2.0
         - myapp-plugin-analytics:v2.0

Keep configuration in version control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Store your ``build-assist.yaml`` files in git to track changes and enable
collaboration.

Validation
----------

rpm-build-assist validates the configuration when it loads. Common errors:

Missing required fields
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ERROR: 'base' is required

**Solution**: Add the missing field.

Invalid YAML syntax
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ERROR: YAML syntax error

**Solution**: Check for:

* Correct indentation (use spaces, not tabs)
* Matching quotes
* Valid YAML structure

Unknown fields
~~~~~~~~~~~~~~

rpm-build-assist ignores unknown fields but may warn about them in verbose
mode.

Next steps
----------

* Learn about :doc:`build_section` configuration
* Understand :doc:`install_section` options
* See :doc:`../tutorial/first_build` for a complete example
