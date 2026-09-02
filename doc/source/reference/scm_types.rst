SCM Types Reference
===================

This page describes each supported SCM (Source Code Management) type.

Overview
--------

The ``type`` field in build source definitions specifies which version control
system to use. Each type has different requirements and behavior.

dist-git
--------

**Description**: Fedora/CentOS/RHEL dist-git repositories

**URL construction**: ``{url}{package}``

**Requirements**:

* Repository follows dist-git layout
* Contains spec file and source metadata
* Uses git for version control

**Branch format**: dist-git branch names (e.g., ``rawhide``, ``f39``, ``epel9``)

**Example**:

.. code-block:: yaml

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide
         - vim:f39

**Full URLs**:

* ``https://src.fedoraproject.org/rpms/htop`` (branch: rawhide)
* ``https://src.fedoraproject.org/rpms/vim`` (branch: f39)

**Repository layout**:

.. code-block:: text

   package/
   ├── package.spec
   ├── sources
   ├── .gitignore
   ├── (metadata files)
   └── *sources.sh          # Optional source-assembly script

**Common repositories**:

* Fedora: ``https://src.fedoraproject.org/rpms/``
* CentOS Stream: ``https://gitlab.com/redhat/centos-stream/rpms/``

**Source handling**:

Sources are assembled during checkout, before the src.rpm is built:

1. Sources listed with a URL are fetched with ``spectool``.
2. If the repository contains a script whose name ends in ``sources.sh``,
   it is run to assemble the remaining sources. Some non-Fedora dist-git
   projects use such a script to generate tarballs (for example from an
   upstream git tag) instead of a lookaside cache.

Both steps run on the host, in the checkout directory. If a source the spec
references is still missing afterwards, src.rpm assembly fails and reports the
missing file. Because these scripts execute during the build, only build from
dist-git repositories you trust.

**Notes**:

* This is the default type if not specified
* Works with ``rpkg`` or ``fedpkg`` tooling
* A ``*sources.sh`` script, when present, is executed automatically

git
---

**Description**: Standard git repositories

**URL construction**: ``{url}{package}``

**Requirements**:

* Repository contains ``{package}.spec`` in the root
* Spec file matches package name
* Sources in repo or downloaded by spec

**Branch format**: git branch names, tags, or commit hashes

**Example**:

.. code-block:: yaml

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:main
         - mylib:v1.0.0
         - another:abc123def

**Full URLs**:

* ``https://github.com/myorg/myapp`` (branch: main)
* ``https://github.com/myorg/mylib`` (tag: v1.0.0)
* ``https://github.com/myorg/another`` (commit: abc123def)

**Repository layout**:

.. code-block:: text

   myapp/
   ├── myapp.spec          # Required
   ├── README.md
   ├── src/
   │   └── (source code)
   └── (other files)

**Spec file location**: Must be ``{package}.spec`` in repository root

**Source handling**: The spec file can either:

1. Package source files from the git repo
2. Download sources using Source0, Source1, etc.

**Common workflows**:

* GitHub projects: ``https://github.com/org/``
* GitLab projects: ``https://gitlab.com/org/``
* Internal git servers: ``https://git.example.com/``

**Notes**:

* Mock's SCM plugin will checkout the specified branch/tag/commit
* The ``write_tar=True`` option creates a tarball from the git checkout

svn
---

**Description**: Subversion repositories

**URL construction**: ``{url}{package}``

**Requirements**:

* Repository contains ``{package}.spec``
* Subversion client installed

**Branch format**: Subversion paths (e.g., ``trunk``, ``branches/v1.0``)

**Example**:

.. code-block:: yaml

   build:
     - type: svn
       url: https://svn.example.com/repos/
       packages:
         - myapp:trunk
         - mylib:branches/stable

**Notes**:

* Less common in modern RPM packaging
* Requires ``svn`` command-line tool

cvs
---

**Description**: CVS repositories

**URL construction**: Varies by CVS setup

**Requirements**:

* Repository contains spec file
* CVS client installed

**Branch format**: CVS tags or branches

**Example**:

.. code-block:: yaml

   build:
     - type: cvs
       url: :pserver:anonymous@cvs.example.com:/repo
       packages:
         - myapp:HEAD

**Notes**:

* Rarely used in modern development
* Requires ``cvs`` command-line tool
* Limited mock support

Comparison table
----------------

.. list-table::
   :header-rows: 1
   :widths: 15 20 25 20 20

   * - Type
     - Use Case
     - Repository Layout
     - Common Repos
     - Popularity
   * - dist-git
     - Fedora/RHEL packages
     - dist-git format
     - Fedora, CentOS
     - High
   * - git
     - Custom packages
     - Spec in root
     - GitHub, GitLab
     - High
   * - svn
     - Legacy projects
     - Spec in root
     - Internal
     - Low
   * - cvs
     - Very old projects
     - Spec in root
     - Internal
     - Very low

Choosing a type
---------------

Use dist-git when
~~~~~~~~~~~~~~~~~

* Building existing Fedora/RHEL/CentOS packages
* Working with standard dist-git workflows
* Contributing to Fedora/CentOS

Use git when
~~~~~~~~~~~~

* Building custom applications
* Source code is in git
* GitHub/GitLab hosted projects

Use svn when
~~~~~~~~~~~~

* Legacy projects use Subversion
* Can't migrate to git

Use cvs when
~~~~~~~~~~~~

* Very old legacy projects
* No other option available

URL patterns
------------

dist-git trailing slash
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # With trailing slash (recommended for dist-git)
   url: https://src.fedoraproject.org/rpms/

   # Without (also works)
   url: https://src.fedoraproject.org/rpms

git repository extensions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # GitHub/GitLab auto-add .git
   url: https://github.com/myorg/

   # Explicit .git extension (also works)
   url: https://github.com/myorg/myapp.git
   packages:
     - myapp:main  # URL becomes: {url}{package}.git

Branch/tag specification
------------------------

Git
~~~

.. code-block:: yaml

   packages:
     - myapp:main              # Branch
     - mylib:v1.0.0            # Tag
     - another:abc123def456    # Commit hash
     - default                 # Defaults to 'main'

dist-git
~~~~~~~~

.. code-block:: yaml

   packages:
     - package:rawhide    # Rawhide branch
     - package:f39        # Fedora 39
     - package:epel9      # EPEL 9
     - package:main       # Main branch (newer)

Troubleshooting
---------------

Repository not found
~~~~~~~~~~~~~~~~~~~~

**Error**: Could not find repository

**Check**:

1. Verify URL construction: ``{url}{package}``
2. Check repository exists
3. Verify you have access (public vs private)

Branch doesn't exist
~~~~~~~~~~~~~~~~~~~~

**Error**: Branch/tag not found

**Solutions**:

* List branches: ``git ls-remote {url}{package}``
* Check branch name spelling
* Verify tag exists

Spec file not found
~~~~~~~~~~~~~~~~~~~

**Error**: Could not find spec file

**Causes** (for git):

* Spec file name doesn't match package name
* Spec file in subdirectory instead of root

**Solution**: Ensure ``{package}.spec`` exists in repository root

Build fails after checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: Build fails after source checkout succeeds

**Common causes**:

* Spec file has errors
* Missing build dependencies
* Source files not available

**Debug**: Check mock logs in ``/var/lib/mock/{config}/result/build.log``

See also
--------

* :doc:`../format/build_section` - Build section configuration
* :doc:`../howto/mixed_sources` - Using multiple source types
* mock SCM plugin documentation
