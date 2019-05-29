.. _Examples:

Examples
========

Runcible Simple
---------------

Runcible Simple is an example DB that shows how MergeDB can be used to generate Runcible network configurations.

The base ``mdb.yaml`` definition in the root directory has the following contents:

.. literalinclude:: ../examples/runcible_simple/mdb.yaml

The ``knockout`` attribute allows layers to stop the inheritance of attributes and keys from higher layers.

We also have two ``keyed_array`` merge rules. These override the default ``simple_array_merge_nodup`` strategy for lists.
We define these rules by specifying the ``path`` (In this case, there is no path, as they are top level keys), the
``attribute`` to match, and a ``key`` to inform the ``keyed_array`` strategy of which key to use to associate inherited
items.

This example has two buildable declarations, ``switch1.yaml`` and ``switch2.yaml``, both located in ``Cumulus_Switches``.

.. literalinclude:: ../examples/runcible_simple/Cumulus_Switches/switch1.yaml

.. literalinclude:: ../examples/runcible_simple/Cumulus_Switches/switch2.yaml

These files only include content, in this case they define runcible layers.

This directory has a ``dir.yaml`` override as well:

.. literalinclude:: ../examples/runcible_simple/Cumulus_Switches/dir.yaml

This file does two things, firstly it specifies that ``switch1`` and ``switch2`` are to be built when mergedb runs.
Secondly, it defines some inherited layers for both built items.  Note that the path for the ``inherit`` attribute is
relative to the root directory, not the current directory.

.. note::
    ``inherit`` only applies to built configs in the current directory, it does not include any intermediate
    layers.

Now lets examine the other directories where the layers are stored. In all of the other directories, we have a blank
``dir.yaml`` file that simply lets MergeDB know that there is content it should index in those directories. Then we have
several intermediate non-built declarations.

.. literalinclude:: ../examples/runcible_simple/Roles/ssh_creds.yaml

This file is just content, once again a runcible layer.

.. literalinclude:: ../examples/runcible_simple/Roles/vlans.yaml

.. literalinclude:: ../examples/runcible_simple/Roles/Switch_Classes/spine.yaml

These files are also content, but they have some jinja2 templating, to reduce the amount of boilerplate inside the layer.

The spine.yaml is also in a subdirectory of roles, this doesn't affect the behavior of Runcible at all, and is just to
show that the user is able to define the directory structure that makes sense for the data that they are organizing.

The result of running ``mergedb examples/runcible_simple build`` on this database is:

.. program-output:: cd .. && python -m mergedb examples/runcible_simple build
    :shell:

One of the important things to note, is that due to the merge rules specified in ``mdb.yaml``, the name of vlan1 was
overridden by the contents of ``spine.yaml``, but it's entry was not duplicated as ``keyed_array_merge`` identified the
duplicate via the key specified in the rule and merged them.