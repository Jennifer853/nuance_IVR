FROM python:3.9
EXPOSE 8080
WORKDIR /root/webService
COPY . .
RUN python3 -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    ACCEPT_EULA=Y apt-get install -y mssql-tools18 && \
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc" && \
    apt-get install -y unixodbc-dev && \
    apt-get install -y libgssapi-krb5-2
CMD python3 app.py