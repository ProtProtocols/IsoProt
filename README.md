# IsoLabeledProtocol

This project is still in a development stage. All resources are only intended to be used for testing. The protocol is based on the following template implementing an environment based on jupyter notebooks: https://github.com/ProtProtocols/protprotocols_template

## Usage
- You need to have docker installed. For more details, see https://docs.docker.com/engine/installation/

- Get the docker image (you might need to be administrator): 
```bash
docker pull veitveit/isolabeledprotocol:latest
```

- Run the image
```bash
docker run -it -p 8888:8888 veitveit/isolabeledprotocol:latest
```

- Open your favorite web browser and access the image via 0.0.0.0:8888

- You can start with the example use case by clicking on the file Example.ipynb


## Development

Change Dockerfile and file structure to add further software tools or jupyter features. 


## ToDo

  - [ ] More detailed description for development
  - [ ] Replace isobar version with one of our's
  - [ ] Output files, which folder structure? General cleanup of files

Planned features:

  - [ ] Add support for more complex experimental setups (ie. grouping of channels)
  - [ ] Add interactive result viewer
