FROM openjdk:17-slim

#install gnu
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code
RUN chmod 777 /code

WORKDIR /code

COPY bash/run_java_code.sh /run_java_code.sh
RUN chmod +x /run_java_code.sh


ENTRYPOINT ["/run_java_code.sh"]