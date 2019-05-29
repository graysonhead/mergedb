Configuration
=============

Concepts
--------

Database
^^^^^^^^

A database in MergeDB is a structured directory containing YAML files. Each database must have an ``mdb.yaml`` and each
sub-directory must have a ``dir.yaml`` in order for it's declarations to be included. Any .yaml file in an included
directory is considered a declaration, and eligible to be built.

Example databases can be found here: https://github.com/graysonhead/mergedb/tree/master/examples

mdb.yaml
--------

When you attempt to build a MergeDB database, MergeDB will look for an ``mdb.yaml`` or ``mdb.yml`` in the root of the
selected directory. This file can be empty, in which case default parameters will be used, but it is required in order
to delineate that the directory is a valid MergeDB database.

Declarations
^^^^^^^^^^^^

Any .yaml in a valid sub-directory is considered a declaration. A declaration has two parts, content and configuration.
Configuration will accept parameters from the MergeDB Configuration Object unless otherwise specified. Any configuration
must be placed under a top-level-key of ``mergedb``, and will override the mergedb configuration for this declaration
only.

For example:

.. literalinclude:: ../examples/keyed_array_merge/layers/layer2.yaml



Built Declarations
^^^^^^^^^^^^^^^^^^

Built declarations are regular declarations that have been added to the build list inside of a ``dir.yaml`` file. They
serve as the "anchor" for inheritance, and are the deliverable of MergeDB. The end result from running the build command
will be a dict containing all of the built declarations, keyed by their filenames. See _Examples for more information.


MergeDB Configuration Object
----------------------------

The mergedb configuration dict can be placed in several different places within mergedb, for example, here is an example
``mdb.yaml`` file.

.. literalinclude:: ../examples/runcible_simple/mdb.yaml

This object accepts the following parameters:

.. data:: knockout = '~'

Accepted Values: Any valid string or ``false``

Setting a knockout string will allow more specific declarations to override values within less specific
declarations. See Knockouts_ for more information.

.. data:: strategy = 'deep_merge'

Accepted Values: ``deep_merge``

Currently, MergeDB only supports deep merging, but eventually several different simpler merge strategies will be
introduced, mainly to be used with merge rules.

.. data:: build = []

Accepted Value: Declaration name in the current directory

Valid only in: ``dir.yaml``

Build declarations are the base unit of MergeDB, any declaration in the build list will have it's inherited declarations
merged and will be output when ``mergedb build`` is run. It can only be specified in the ``dir.yaml`` in the same
relative path as the declarations it specifies.

.. data:: inherit = []

Accepted Value: Path to declaration relative to mdb.yaml

Inherit allows you to list the paths of other declarations in order to have them merged. This option, like all, is
inherited, so specifying it in your mdb.yaml will cause all built declarations within your whole database to inherit
those declarations.

Merge Rules
-----------

Merge rules are a set of rules that can be specified in the configuraton object that can override the default merge
behavior.

Keyed Array
^^^^^^^^^^^

Keyed Array merge rules modify the default merging behavior of arrays. You would use a keyed array merge in the case
where you have a list of dicts that can each be identified by a unique key attribute. This key attribute is used by the
keyed array merge strategy to perform a merge operation on the individual items within the array, using their key to
associate them with each other.

For example:

.. literalinclude:: ../examples/keyed_array_merge/layers/layer1.yaml

.. literalinclude:: ../examples/keyed_array_merge/layers/layer2.yaml

.. literalinclude:: ../examples/keyed_array_merge/layers/dir.yaml

Will result in


.. program-output:: cd .. && python -m mergedb examples/keyed_array_merge build
    :shell:

.. _Knockouts:

Knockouts
---------

Using a knockout character will result in the less specific data at that key being wiped out, for example:

.. literalinclude:: ../examples/minimal/layers/layer1.yaml

.. literalinclude:: ../examples/minimal/layers/layer2.yaml


Will result in:

.. program-output:: cd .. && python -m mergedb examples/minimal build
    :shell:


