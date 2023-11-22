# OMERO.mdv

OMERO.web plugin to add [Multi-Dimensional Viewer](https://mdv.molbiol.ox.ac.uk/)
to the OMERO-web framework.

NB: Currently this is a very early experimental app. It allows you to choose a single OMERO.table attached to a Project or Dataset using the "Open with... MDV" menu.

Screenshot showing data from [idr0021](https://idr.openmicroscopy.org/webclient/?show=project-51)
displaying analysis results prepared for a [training workshop](https://omero-guides.readthedocs.io/en/latest/parade/docs/omero_parade.html).

<img src="https://user-images.githubusercontent.com/900055/245738983-969b86c9-f44b-479d-8abe-3b20e568cf5d.png" alt="Screenshot 2023-06-14 at 10 04 25" style="max-width: 100%;">


# Install

This requires `omero-py`. See instructions at https://github.com/ome/omero-py to create
your python environment. Then, in the same python environment, clone this repo and install:

```
    $ cd omero-mdv
    $ pip install -e .

    $ omero config append omero.web.apps '"omero_mdv"'

    $ omero config append omero.web.open_with '["MDV", "mdv_choose_data", {"supported_objects": ["project", "dataset"]}]'

    $ omero config append omero.web.ui.top_links '["MDV", "open_mdv", {"title": "Open Multi-Dimensional-Viewer", "target": "_blank"}]'

```

MDV requires particular http headers to allow `SharedArrayBuffers` to work in the browser.
These headers need to be included in the `nginx` config (will need to regenerate the
config and restart omero-web after these steps):

```
    $ omero config append omero.web.nginx_server_extra_config '"add_header Cross-Origin-Opener-Policy same-origin;"'
    $ omero config append omero.web.nginx_server_extra_config '"add_header Cross-Origin-Embedder-Policy require-corp;"'
```

# Running Django dev server

When running the development devserver, we need force the processing of static
requests via the Middleware which adds the http headers above. This can be achieved with
the Django `runserver --nostatic` option.
For example, when running omero-web from source:

```
    $ git clone https://github.com/ome/omero-web
    $ cd omero-web
    $ pip install -e .
    $ python omeroweb/manage.py runserver 4080 --nostatic
```
Then go to http://localhost:4080/


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


# Sample demo data

Check the `docs` directory for instructions on how to find and import sample data that
can be used to demonstrate or test the OMERO.mdv app.
