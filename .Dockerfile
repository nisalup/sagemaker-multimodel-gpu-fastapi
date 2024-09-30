# An exampe dummy dockerfile that can be used as a base for the final dockerfile
# Note that the base dockerfile should be compatible with Sagemaker
FROM nvidia/cuda:12.6.1-cudnn-base-ubuntu22.04

# Set a docker label to enable container to use SAGEMAKER_BIND_TO_PORT
# environment variable if present
LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    # generic requirements
    nginx


RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    numpy


ENV FORCE_CUDA="1"

# Set the working directory to /
WORKDIR /app/

# copy the source code
COPY sm_multimodel_gpu_fastapi/ /app/

# copy nginx conf
COPY nginx.conf /app/nginx.conf

# copy manually and make the entrypoint executable
COPY dockerd-entrypoint.py /usr/local/bin/dockerd-entrypoint.py
RUN chmod +x /usr/local/bin/dockerd-entrypoint.py

# Make port 8080 available to the world outside this container
ENV SAGEMAKER_BIND_TO_PORT=8080

EXPOSE 8080

ENTRYPOINT ["python", "/usr/local/bin/dockerd-entrypoint.py"]

CMD ["serve"]
