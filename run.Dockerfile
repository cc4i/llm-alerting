FROM gcr.io/buildpacks/gcp/run:google-22
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
  imagemagick && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
  mv kubectl /usr/local/bin/kubectl && \
  chmod +x /usr/local/bin/kubectl
USER cnb