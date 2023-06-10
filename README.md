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

