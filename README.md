# IsoLabeledProtocol

This project provides a reproducible pipeline to analyse isobarically labelled mass spectrometry based quantitative proteomics data.

The different workflows are created using the [jupyter notebook](http://jupyter.org) environment. They look like normal documents with interactive elements (like buttons, etc.) in them and are based on our [standard workflow template](https://github.com/ProtProtocols/protprotocols_template). Thereby, they also provide completely reproducible records of the bioinformatic pipeline used to analyse the data.

The pipelines are made available as [Docker](https://www.docker.com) containers. These are light-weight virtual machines that contain the complete software necessary to run the pipeline. Thereby, you do not have to worry about installing any additional required software.

This project is **still under development**. All resources are only intended to be used for testing. We are simply not done yet.

## Usage
- You need to have docker installed. For more details, see https://docs.docker.com/engine/installation/

The following commands have to be execute in your operating systems command prompt.

- Get the docker image (you might need to be administrator): 
```bash
docker pull veitveit/isolabeledprotocol:latest
```

- Run the image
```bash
docker run -it -p 8888:8888 veitveit/isolabeledprotocol:latest
```
or, to mirror your current folder onto _/data_ and the output folder in the docker to _OUT_ in your folder
```bash
docker run -it -p 8888:8888 -v ./:/data/ -v ./OUT:/home/biodocker/OUT veitveit/isolabeledprotocol:latest
```


- Open your favorite web browser and access the image via 0.0.0.0:8888

- You can start with the example use case by clicking on the file Isobaric_Workflow.ipynb

## Feedback

In case you have any questions about using the pipeline or find an issue, please simply [submit an issue](https://github.com/ProtProtocols/IsoLabeledProtocol/issues) through this GitHub page.
