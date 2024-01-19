FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.28

COPY . ./

RUN python3 -m pip install --no-cache-dir notebook jupyterlab

RUN pip install --no-cache-dir -r requirements.txt
