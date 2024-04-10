FROM gcr.io/buildpacks/google-22/run:latest
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
  apt-transport-https ca-certificates gnupg curl && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
  apt-get update && apt-get install google-cloud-cli && \
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
  mv kubectl /usr/local/bin/kubectl && \
  chmod +x /usr/local/bin/kubectl
USER cnb