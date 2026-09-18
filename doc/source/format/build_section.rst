Build Section Reference
=======================

The ``build`` section defines source repositories and packages to build.

Structure
---------

The ``build`` section is a list of source definitions:

.. code-block:: yaml

   build:
     - type: <scm-type>
       url: <base-url>
       packages:
         - <package>:<branch>

Each source definition specifies a repository type, base URL, and list of
packages to build from that repository.

Fields
------

type
~~~~

**Required**: No

**Default**: ``dist-git``

**Type**: String

**Description**: The SCM (Source Code Management) method to use.

**Supported values**:

* ``dist-git`` - Fedora/CentOS/RHEL dist-git repositories
* ``git`` - Standard git repositories
* ``svn`` - Subversion repositories
* ``cvs`` - CVS repositories

See :doc:`../reference/scm_types` for details on each type.

**Example**:

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide

url
~~~

**Required**: Yes

**Type**: String (URL)

**Description**: Base URL for repositories. Package names are appended to
this URL to form the full repository path.

For ``dist-git``, the full URL is: ``{url}{package}``

For other types, the URL construction may vary by SCM type.

**Example**:

.. code-block:: yaml

   # For dist-git
   url: https://src.fedoraproject.org/rpms/
   # Package 'htop' → https://src.fedoraproject.org/rpms/htop

   # For git
   url: https://github.com/myorg/
   # Package 'myapp' → https://github.com/myorg/myapp

packages
~~~~~~~~

**Required**: Yes

**Type**: List of strings

**Description**: List of packages to build from this repository.

**Format**: ``package-name:branch``

* If ``:branch`` is omitted, ``main`` is used as the default
* The branch can be a branch name, tag, or commit hash (depending on SCM type)

**Example**:

.. code-block:: yaml

   packages:
     - myapp:main           # Branch 'main'
     - mylib:v1.0.0         # Tag 'v1.0.0'
     - another-package      # Defaults to 'main'

with
~~~~

**Required**: No

**Type**: String or list of strings

**Description**: Enable RPM conditional-build (``%bcond``) options, one per
value. Each becomes a ``mock --with=<name>`` argument applied to every package
in this source, at both src.rpm assembly and the binary build, so spec
conditionals resolve consistently.

without
~~~~~~~

**Required**: No

**Type**: String or list of strings

**Description**: Disable RPM conditional-build (``%bcond``) options, the inverse
of ``with``. Each value becomes a ``mock --without=<name>`` argument.

define
~~~~~~

**Required**: No

**Type**: String or list of strings

**Description**: Define arbitrary RPM macros. Each value is a
``macro-name value`` pair and becomes a ``mock --define=<value>`` argument.

**Example**:

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       with: [python3, docs]     # --with=python3 --with=docs
       without: tests            # --without=tests
       define: "debug_package 1" # --define=debug_package 1
       packages:
         - htop:rawhide
         - vim:rawhide

Because these flags apply to the whole source definition, build packages that
need different flags under separate source definitions (repeating the same
``type`` and ``url``).

Multiple source definitions
---------------------------

You can have multiple source definitions to build from different repositories:

.. code-block:: yaml

   build:
     # Fedora dist-git packages
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide
         - postgresql:f39

     # Custom GitHub packages
     - type: git
       url: https://github.com/myorg/
       packages:
         - webapp:v2.0
         - webapp-utils:v2.0

     # Internal packages
     - type: git
       url: https://git.internal.example.com/
       packages:
         - company-theme:main

Build order
-----------

Packages are built in the order they appear in the configuration file.

Within a single source definition, packages are built in list order.

Across source definitions, each source's packages are built in sequence.

**Example**:

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         - lib1:main    # Built 1st
         - lib2:main    # Built 2nd

     - url: https://github.com/other/
       packages:
         - app:main     # Built 3rd

This ensures dependencies are built before packages that depend on them.

Dependency resolution
---------------------

Mock's ``--chain`` mode is used, which means:

* Each package is built in order
* Later packages can depend on earlier packages
* Dependencies are resolved from the local repository
* Earlier packages' RPMs are available when building later packages

**Example**:

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         - mylib:v1.0      # Provides libmylib.so
         - myapp:v1.0      # BuildRequires: mylib

When building ``myapp``, the ``mylib`` RPM is already in the local repository
and will be used to satisfy the build dependency.

SCM-specific behavior
---------------------

dist-git
~~~~~~~~

For dist-git repositories:

* Expects a standard dist-git layout with spec file and sources
* Uses ``rpkg`` or similar tools internally
* The ``branch`` corresponds to dist-git branches (e.g., ``rawhide``, ``f39``)
* Online sources are fetched with ``spectool``; a ``*sources.sh`` script in the
  repository, if present, is run to assemble the rest. See
  :doc:`../reference/scm_types` for details.

git
~~~

For regular git repositories:

* Expects a spec file in the repository root
* The spec file name should match the package name
* Sources can be in the repo or downloaded by the spec

The repository must contain:

.. code-block:: text

   mypackage/
   ├── mypackage.spec
   └── (optional source files)

svn and cvs
~~~~~~~~~~~

Similar to git, but using svn or cvs for version control.

Examples
--------

Basic dist-git build
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide
         - vim:f39

Multiple repositories
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide

     - type: git
       url: https://github.com/company/
       packages:
         - webapp:v2.0

Dependency chain
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - base-lib:v1.0
         - utility-lib:v1.0
         - main-app:v1.0

The packages are built in order, so ``main-app`` can depend on both libraries.

Best practices
--------------

Order by dependencies
~~~~~~~~~~~~~~~~~~~~~

List packages in dependency order:

.. code-block:: yaml

   packages:
     - library:main        # No dependencies
     - middleware:main     # Depends on library
     - application:main    # Depends on middleware

Group by source
~~~~~~~~~~~~~~~

Group packages from the same repository in one source definition:

.. code-block:: yaml

   # Good: One source definition per repository
   build:
     - url: https://github.com/org1/
       packages:
         - pkg1:main
         - pkg2:main

   # Works but verbose
   build:
     - url: https://github.com/org1/
       packages:
         - pkg1:main
     - url: https://github.com/org1/
       packages:
         - pkg2:main

Use specific branches/tags
~~~~~~~~~~~~~~~~~~~~~~~~~~

For reproducibility, use specific tags or commit hashes rather than branch
names:

.. code-block:: yaml

   packages:
     - myapp:v2.0.1    # Specific release tag
     # vs
     - myapp:main      # Moving target

Common issues
-------------

Package not found
~~~~~~~~~~~~~~~~~

**Error**: ``ERROR: Could not find package at URL``

**Causes**:

* URL construction is incorrect
* Package name doesn't match repository name
* Branch doesn't exist

**Solution**: Verify the full URL by appending the package name to the base
URL and checking it in a browser or with git.

Build failures due to missing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: Build fails with missing dependencies

**Causes**:

* Packages are in wrong order
* Dependency is not in the build list
* Dependency is external (not being built)

**Solution**:

* Reorder packages
* Add missing package to build list
* Use ``addrepo`` to provide external dependencies

Spec file not found
~~~~~~~~~~~~~~~~~~~

**Error**: ``ERROR: Could not find spec file``

**Causes** (for git type):

* Spec file name doesn't match package name
* Spec file is in a subdirectory

**Solution**: Ensure ``package-name.spec`` is in the repository root.

Next steps
----------

* See :doc:`../reference/scm_types` for details on each SCM type
* Learn about :doc:`install_section` for post-build steps
* Read :doc:`../howto/mixed_sources` for complex scenarios
