# OMERO.mdv

OMERO.web plugin to add [Multi-Dimensional Viewer](https://mdv.molbiol.ox.ac.uk/)
to the OMERO-web framework.

NB: Currently this is a very early experimental app. It allows you to choose a single OMERO.table attached to a Project or Dataset using the "Open with... MDV" menu.

Screenshot showing data from [idr0021](https://idr.openmicroscopy.org/webclient/?show=project-51)
displaying analysis results prepared for a [training workshop](https://omero-guides.readthedocs.io/en/latest/parade/docs/omero_parade.html).

<img src="https://user-images.githubusercontent.com/900055/245738983-969b86c9-f44b-479d-8abe-3b20e568cf5d.png" alt="Screenshot 2023-06-14 at 10 04 25" style="max-width: 100%;">


# Install


```
    $ cd omero-mdv
    $ pip install -e .

    $ omero config append omero.web.apps '"omero_mdv"'

    $ omero config append omero.web.open_with '["MDV", "mdv_choose_data", {"supported_objects": ["project", "dataset"]}]'

```

# Headers

MDV requires particular headers to allow SharedArrayBuffers to work in the browser.
These will be added by Django Middleware but are not included for static requests.
When deployed in production, these headers should be added by NGINX.

```
    Cross-Origin-Opener-Policy: same-origin
    Cross-Origin-Embedder-Policy: require-corp
```

When running the development devserver, we need force the processing of static
requests via the Middleware, which can be achieved with `--nostatic`, e.g:

```
    $ python omeroweb/manage.py runserver 4080 --nostatic
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

