FROM gcc:13.2.0

# install gnu
RUN apt-get update && apt-get install -y time bc && rm -rf /var/lib/apt/lists/*

RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code

WORKDIR /code

COPY bash/run_c_code.sh /run_c_code.sh
RUN chmod +x /run_c_code.sh

USER runner

ENTRYPOINT [ "/run_c_code.sh" ]