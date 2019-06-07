# How to launch GroupPowerSaveServer

1. `python -m GroupPowerSaveServer`

# How to launch TestClient

1. Run `python -m TestClient -h` to see available options

# How to launch TestClient in a jupyter lab environment

1. Install [jupyter lab](https://jupyterlab.readthedocs.io/en/stable/index.html) / [jupyter lab ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) / [jupyter lab sidecar](https://github.com/jupyter-widgets/jupyterlab-sidecar) 
2. Run `jupyter lab`
3. Run GroupPowerSaveServer on local or cloud
4. Open `TestClients.ipynb` in a jupyter lab and be sure to set correct `target_server`
5. Don't forget to run 4th cell per each try to terminate the client