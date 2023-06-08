# OMERO.mdv

OMERO.web plugin to add [Multi-Dimensional Viewer](https://mdv.molbiol.ox.ac.uk/)
to the OMERO-web framework.


# Install


```
    $ cd omero-mdv
    $ pip install -e .

    $ omero config append omero.web.apps '"omero_mdv"'

    $ omero config append omero.web.open_with '["MDV", "mdv_index", {"supported_objects": ["project", "dataset"]}]'

```