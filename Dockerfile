FROM python:3.9

WORKDIR /app

COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
ENV NAME scinamic

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Install Nano text editor
RUN apt-get update && \
    apt-get install -y nano && \
    rm -rf /var/lib/apt/lists/*
#ENTRYPOINT ["/entrypoint.sh"]
#CMD ["sleep","infinity"]
