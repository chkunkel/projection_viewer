# DANGER
# this is our first build stage, it will not persist in the final image
FROM ubuntu as intermediate

# install git
RUN apt-get update
RUN apt-get install -y git

# add credentials on build
ARG SSH_PRIVATE_KEY
ARG SSH_PRIVATE_KEY2
RUN mkdir /root/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
#RUN echo "${SSH_PRIVATE_KEY2}" > /root/.ssh/id_rsa2
RUN chmod 700 /root/.ssh/id_rsa
#RUN chmod 700 /root/.ssh/id_rsa2
RUN eval "$(ssh-agent -s)"

# make sure your domain is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

## add the second key
#RUN ssh-add /root/.ssh/id_rsa2

RUN git clone --depth 1 --recursive git@github.com:stenczelt/projection_viewer.git


RUN echo "${SSH_PRIVATE_KEY2}" > /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh/id_rsa
RUN git clone --depth 1 --recursive git@github.com:stenczelt/ASAP.git

# END OF DANGER
# ------------------------------------------------------------------------

FROM continuumio/miniconda3
LABEL maintainer="Tamas K. Stenczel <tks32@cam.ac.uk>"

# copy the repository form the previous image
COPY --from=intermediate /projection_viewer /opt/projection_viewer
COPY --from=intermediate /ASAP /opt/ASAP

RUN apt-get update; \
    apt-get install -y vim gcc build-essential

#RUN git clone --depth 1 --recursive git@github.com:stenczelt/projection_viewer.git
#RUN git clone --depth 1 --recursive git@github.com:stenczelt/ASAP.git

RUN conda env create -f /opt/projection_viewer/docker/env.yml    # env given
#RUN conda init --all
#RUN conda activate projection
RUN echo "source activate projection" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH


#RUN pip install git+https://github.com/plotly/dash-bio-utils.git
RUN git clone --depth 1 --recursive https://github.com/plotly/dash-bio-utils.git /opt/dash-bio-utils && cd /opt/dash-bio-utils && python setup.py install
RUN pip install git+https://github.com/stenczelt/dash-bio.git
RUN pip install git+https://github.com/libAtoms/abcd.git

RUN cd /opt/projection_viewer && python setup.py install
#RUN abcd login mongodb://localhost

WORKDIR /opt/
#RUN git clone --depth 1 --recursive https://github.com/stenczelt/dash-bio.git
#RUN git clone --depth 1 --recursive https://github.com/plotly/dash-bio-utils.git
# this one needs a deploy key


#git@github.com:stenczelt/projection_viewer.git

# install dash-bio
#RUN cd dash-bio-utils; python setup.py install
#RUN cd dash-bio; python setup.py install
# maybe:




