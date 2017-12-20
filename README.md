# IsoLabeledProtocol

This project is still in a development stage. All resources are only intended to be used for testing.

## Installation

To build the Docker image on a linux (tested on Ubuntu) system you can use the `DockerSetup/rebuild_docker.sh` script.

This script is expected to be executed from the root directory:

```bash
test@mashine:/tmp/IsoLabeledProtocol$ DockerSetup/rebuild_docker.sh
```

## Testing

To launch the docker image you can use `Test/run_docker.sh` script. Again, this was only tested on Ubuntu.

To then launch the pipeline use:

```bash
# Run the search
biodocker@JG-T460s:/data$ Scripts/pipeline.sh -d Test/sp_human.fasta -p 20 -f 0.05 -c 1 Test/test.mgf

# Analyse the result
biodocker@JG-T460s:/data$ Rscript Scripts/isobar_analysis.R pipeline-test/experiment1_test_1_Extended_PSM_Report.txt pipeline-test/test.mgf
```

This will only execute the search and the result generation. The resulting `

## Structure

The repository is structured in the following way:

  * **DockerSetup:** Files / Scripts required to build the docker image
  * **Test**: Files and Scripts used for testing the pipeline
  * **Scripts**: The analysis pipeline related scripts. These scripts are currently not added to the docker image to simplify the development. At a later stage, these should be included in the image.

## ToDo

  - [ ] Change statically typed variables to command line parameters
  - [ ] Replace isobar version with one of our's

Planned features:

  - [ ] Add support for more complex experimental setups (ie. grouping of channels)
    - This probably requires a web-based interface to take the different numbers of channels per quant strategy into consideration
  - [ ] Replace `pipeline.sh` script by web-based Python application
  - [ ] Add RShiny based result viewer application
