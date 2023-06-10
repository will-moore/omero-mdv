# OMERO.mdv

OMERO.web plugin to add [Multi-Dimensional Viewer](https://mdv.molbiol.ox.ac.uk/)
to the OMERO-web framework.


# Install


```
    $ cd omero-mdv
    $ pip install -e .

    $ omero config append omero.web.apps '"omero_mdv"'

    $ omero config append omero.web.open_with '["MDV", "mdv_choose_data", {"supported_objects": ["project", "dataset"]}]'

```

# Update MDV viewer

The MDV viewer html and static assets are hosted in this repo
under `templates/mdv/index.html` and `omero_mdv/static/mdv/`

We need to build the MDV viewer to use relative links to static assets.
This is currently configured on this branch: https://github.com/will-moore/MDV/tree/vite_config_base

Checkout that branch (rebase if desired), then build and copy assets to this repo:

```
    $ npm install
    $ npm run vite-build

    $ cp -r vite-dist/assets/ /path/to/omero-mdv/omero_mdv/static/mdv/assets/
    $ cp vite-dist/index.html /path/to/omero-mdv/omero_mdv/templates/mdv/
```

