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
RUN chmod 700 /root/.ssh/id_rsa
RUN eval "$(ssh-agent -s)"

# make sure your domain is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# get the repo, this is private and hence the key is needed
# fixme: change the branch when merger happens
RUN git clone --depth 1 --branch=dev_docker --single-branch git@github.com:chkunkel/projection_viewer.git
#RUN git clone --depth 1 --branch=merger --single-branch git@github.com:stenczelt/projection_viewer.git

# END OF DANGER
# ------------------------------------------------------------------------

FROM continuumio/miniconda3
LABEL maintainer="Tamas K. Stenczel <tks32@cam.ac.uk>"

# copy the repository form the previous image
COPY --from=intermediate /projection_viewer /opt/projection_viewer

RUN apt-get update; \
    apt-get install -y vim gcc build-essential

RUN conda update -n base -c defaults conda
RUN conda env update -n=base --file=/opt/projection_viewer/docker/env.yml    # env given
RUN echo "source activate base" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

#RUN conda install -c conda-forge dscribe=0.2.9
RUN git clone --depth 1 --recursive https://github.com/plotly/dash-bio-utils.git /opt/dash-bio-utils && cd /opt/dash-bio-utils && python setup.py install
RUN pip install git+https://github.com/chkunkel/dash-bio.git
RUN pip install git+https://github.com/libAtoms/abcd.git
RUN pip install git+https://github.com/BingqingCheng/ASAP.git

RUN cd /opt/projection_viewer && python setup.py install

RUN echo "{\"url\": \"mongodb://abcd-mongodb-net\"}" > /root/.abcd
WORKDIR /opt/
