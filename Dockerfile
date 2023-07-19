FROM python:3

LABEL Name=smart_birth Version=0.0.1
EXPOSE 8000

WORKDIR /app
ADD . /app
# ADD ./eb_abhijeet /root/.ssh/id_rsa


# Install libreoffice and sshpass
RUN apt-get -y update && apt-get install sshpass -y 

#install firefox web


# # Using pip:
RUN python -m pip install -r requirements.txt




