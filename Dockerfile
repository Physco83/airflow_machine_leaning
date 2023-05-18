FROM apache/airflow:2.5.1
COPY requirements.txt /
COPY ./java /java
RUN pip install --no-cache-dir -r /requirements.txt
    
ENV JAVA_HOME /java/java-11-openjdk-amd64
RUN export JAVA_HOME