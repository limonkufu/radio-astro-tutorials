FROM artefact.skao.int/ska-build-python:0.1.1

# User setup
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
ENV PATH ${HOME}/.local/bin/:${PATH}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

WORKDIR ${HOME}
USER ${USER}

RUN pip install --no-cache-dir notebook jupyterlab

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir ipywidgets numpy matplotlib scipy

COPY . ${HOME}/