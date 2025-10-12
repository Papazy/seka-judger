FROM gcc:13.2.0

# insta GNU time
RUN apt-get update && apt-get install -y time bc && rm -rf /var/lib/apt/lists/*

RUN useradd -m runner
RUN mkdir /code && chown -R runner:runner /code

WORKDIR /code

COPY bash/run_cpp_code.sh /run_cpp_code.sh
RUN chmod +x /run_cpp_code.sh

USER runner

ENTRYPOINT [ "/run_cpp_code.sh" ]