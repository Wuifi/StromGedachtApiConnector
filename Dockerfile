#FROM python:3.10.7-slim-bullseye
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN python3 -m pip install --upgrade pip
# Install any needed packages specified in requirements.txt
#RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN pip install --index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt 
#--trusted-host pypi.python.org
# run daemon
CMD [ "python3", "./sgamc.py" ]

# EOF

