FROM continuumio/miniconda3
LABEL maintainer="Tamas K. Stenczel <tks32@cam.ac.uk>"

RUN apt-get update; \
    apt-get install -y vim gcc build-essential
RUN conda env create -f env.yml    # env given

RUN pip install git+https://github.com/plotly/dash-bio-utils.git
RUN pip install git+https://github.com/stenczelt/dash-bio.git
RUN pip install git+https://github.com/libAtoms/abcd.git

WORKDIR /opt/
#RUN git clone --depth 1 --recursive https://github.com/stenczelt/dash-bio.git
#RUN git clone --depth 1 --recursive https://github.com/plotly/dash-bio-utils.git
# this one needs a deploy key
RUN git clone --depth 1 --recursive https://github.com/stenczelt/projection_viewer.git
RUN git clone --depth 1 --recursive https://github.com/stenczelt/ASAP.git

# install dash-bio
#RUN cd dash-bio-utils; python setup.py install
#RUN cd dash-bio; python setup.py install
# maybe:




