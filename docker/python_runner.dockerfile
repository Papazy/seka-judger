FROM python:3.12-slim

# install GNU time (paketnya bernama 'time')
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

# create non root user
RUN useradd -m runner
RUN mkdir /code
RUN chown -R runner:runner /code
RUN chmod 777 /code

WORKDIR /code

# copy script & beri izin eksekusi (sebagai root)
COPY bash/run_python_code.sh /run_python_code.sh
RUN chmod +x /run_python_code.sh

# baru pindah ke user non-root
USER runner

ENTRYPOINT ["/run_python_code.sh"]
