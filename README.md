# IsoProt

This project provides a reproducible pipeline to analyse isobarically labelled mass spectrometry based quantitative proteomics data.

<img src="./misc/iso_protocol.svg" width=250 />

The different workflows are created using the [jupyter notebook](http://jupyter.org) environment. They look like normal documents with interactive elements (like buttons, etc.) in them and are based on our [standard workflow template](https://github.com/ProtProtocols/protprotocols_template). Thereby, they also provide completely reproducible records of the bioinformatic pipeline used to analyse the data.

The pipelines are made available as [Docker](https://www.docker.com) containers. These are light-weight virtual machines that contain the complete software necessary to run the pipeline. Thereby, you do not have to worry about installing any additional required software.

This project is **still under development**. All resources are only intended to be used for testing. We are simply not done yet.

## Installation / Usage

### Requirements

- You need to have the docker engine installed. For more details, see https://docs.docker.com/engine/installation/
  In the case of not having a compatible operating system (e.g. Windows 7), you need to install the _Docker Toolbox_: https://docs.docker.com/toolbox/toolbox_install_windows/#what-you-get-and-how-it-works

### docker-launcher

The easiest way to run ProtProtocol protocols is through our [docker-launcher](https://github.com/ProtProtocols/docker-launcher) application. It provides a simple graphical user interface that takes care of downloading the protocol and launching the docker image taking care of all required parameters. As it is a [Java](https://www.java.com) application it supports Windows, Mac OS X, and Linux.

### Manual launch

To launch docker images manually, you need to open your operating system's command prompt (ie. PowerShell on Windows). The docker commands are the same on all operating systems.

- Download the latest stable version of the protocol (you might need to be administrator): 
```bash
docker pull veitveit/isolabeledprotocol:release-0.1
```
- Download the latest development version of the protocol (you might need to be administrator): 
```bash
docker pull veitveit/isolabeledprotocol:latest
```

- Run the image (add :"release-x" or :"latest" when you have downloaded both versions)
```bash
docker run -it -p 8888:8888 veitveit/isolabeledprotocol
```

In order to directly access your computer's folders through the docker image (recommended option) map local directories
to the containers _/data_ (for input data) and _OUT_ (for output data) folders:

```bash
docker run -it -p 8888:8888 -v /path/to/my/mgf/files:/data/ -v /path/to/my/result/folder:/home/biodocker/OUT veitveit/isolabeledprotocol
```

**Note**: When running Docker Toolbox (ie. only available version on Windows 7), local paths must be below _C:\Users_. Additionally, paths need to specified in the following format:
```
# to map C:\Users\Johannes\Downloads
docker run -it -p 8888:8888 -v /c/users/johannes/downloads:/data/ -v /c/users/johannes/results:/home/biodocker/OUT veitveit/isolabeledprotocol
```
- Open your favorite web browser and access the image via 0.0.0.0:8888

- You can start with the example use case by clicking on the file Isobaric_Workflow.ipynb

## Releases

Release 0.1: First fully functional version for analyzing iTRAQ/TMT data.

## Feedback

In case you have any questions about using the pipeline or find an issue, please simply [submit an issue](https://github.com/ProtProtocols/IsoProt/issues) through this GitHub page.

## Development

Any code fixes / enhancements are highly welcome as pull requests.

### Repository directory structure

Jupyter notebooks (.ipnyb) files are kept in the main directory.

  * DockerSetup: files related to building the docker image
  * RELEASE: (deprecated) Directory to bundle release files. This functionality has been taken over by [docker-launcher](https://github.com/ProtProtocols/docker-launcher)
  * Scripts: Collection of python modules that provide functionality shared between protocols (display of GUI for search parameters, etc.)
  * Test: Example dataset to test the pipeline
  * misc: Images etc. to make things look nice

## Acknowledgements

<img src="misc/flag_yellow_low.png" height="200" /><img src="misc/LOGO-ERC.jpg" height="200" />

This project has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme under grant agreement No 788042.
