Variables
=========

.. note::

   Variable support is planned for a future version of rpm-build-assist.
   This documentation describes the planned feature.

Variables will allow you to define reusable values in your configuration
and reference them throughout your YAML file.

Planned syntax
--------------

Define variables:

.. code-block:: yaml

   variables:
     version: "2.0"
     branch: "main"
     org: "mycompany"

Reference variables:

.. code-block:: yaml

   build:
     - url: https://github.com/%{org}/
       packages:
         - myapp:%{branch}
         - myapp-v%{version}:%{branch}

Variable support is planned for a future version of rpm-build-assist.
