FROM veitveit/protprotocols_template:latest

USER root

# Install libraries needed by isobar, ...
RUN apt-get update &&   apt-get install -y apt-transport-https libxml2-dev r-cran-rmysql libnetcdf-dev
#&&  echo "deb https://cran.wu.ac.at/bin/linux/ubuntu xenial/" >> /etc/apt/sources.list &&  apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9 &&  apt-get update &&    apt-get install -y libcurl4-openssl-dev libssl-dev libxml2-dev r-base r-base-dev 

# Setup R
ADD DockerSetup/install_packages.R /tmp/
RUN Rscript /tmp/install_packages.R && rm /tmp/install_packages.R && ls()

# Install Mono
RUN apt-get update && apt-get install -y mono-complete

# Install SearchGui and PeptideShaker
USER biodocker

RUN mkdir /home/biodocker/bin
RUN PVersion=1.16.17 && ZIP=PeptideShaker-${PVersion}.zip && \
    wget -q http://genesis.ugent.be/maven2/eu/isas/peptideshaker/PeptideShaker/${PVersion}/$ZIP -O /tmp/$ZIP && \
    unzip /tmp/$ZIP -d /home/biodocker/bin/ && rm /tmp/$ZIP && \
    bash -c 'echo -e "#!/bin/bash\njava -jar /home/biodocker/bin/PeptideShaker-${PVersion}/PeptideShaker-${PVersion}.jar $@"' > /home/biodocker/bin/PeptideShaker && \
    chmod +x /home/biodocker/bin/PeptideShaker
    
RUN SVersion=3.2.20 && ZIP=SearchGUI-${SVersion}-mac_and_linux.tar.gz && \
    wget -q http://genesis.ugent.be/maven2/eu/isas/searchgui/SearchGUI/${SVersion}/$ZIP -O /tmp/$ZIP && \
    tar -xzf /tmp/$ZIP -C /home/biodocker/bin/ && \
    rm /tmp/$ZIP && \
    bash -c 'echo -e "#!/bin/bash\njava -jar /home/biodocker/bin/SearchGUI-$SVersion/SearchGUI-$SVersion.jar $@"' > /home/biodocker/bin/SearchGUI && \
    chmod +x /home/biodocker/bin/SearchGUI

ENV PATH /home/biodocker/bin/SearchGUI:/home/biodocker/bin/PeptideShaker:$PATH

WORKDIR /home/biodocker/

COPY Example.ipynb .
COPY Example_isobar.ipynb .
COPY Test/test.mgf IN
COPY Test/sp_human.fasta IN

USER root

RUN chown -R biodocker .

# Testing
#RUN pip install jupyter_contrib_nbextensions && jupyter contrib nbextension install --user && pip ins#tall jupyter_nbextensions_configurator && jupyter nbextensions_configurator enable --sys-prefix 
#COPY notebook.json .jupyter/nbconfig/

USER biodocker


# Run example notebook to have the results ready
#RUN jupyter nbconvert --to notebook --ExecutePreprocessor.timeout=3600 --execute Example.ipynb && mv Example.nbconvert.ipynb Example.ipynb && jupyter trust Example.ipynb
