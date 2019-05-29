Configuration
=============

MergeDB Configuration
---------------------

The mergedb configuration dict can be placed in several different places within mergedb, for example, here is an example
``mdb.yaml`` file.

.. literalinclude:: ../examples/runcible_simple/mdb.yaml

This object accepts the following parameters:

.. data:: knockout = '~'

Accepted Values: Any valid string or ``false``

Setting a knockout string will allow more specific declarations to override values within less specific
declarations. See `knockouts` for more information.

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

mdb.yaml
--------

When you attempt to build a MergeDB database, MergeDB will look for an ``mdb.yaml`` or ``mdb.yml`` in the root of the
selected directory. This file can be empty, in which case default parameters will be used, but it is required in order
to delineate that the directory is a valid MergeDB database.

dir.yaml
--------

In each subdirectory of the database, a ``dir.yaml`` or ``dir.yml`` must exist. This