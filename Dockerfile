FROM python:3.11.5-bullseye AS env-build
COPY server/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

FROM python:3.11.5-slim-bullseye
COPY --from=env-build /usr/local/bin/ /usr/local/bin/
COPY --from=env-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
WORKDIR /app/
COPY ./db-init/ /tmp/db-init/
COPY ./server/ ./db-init/schema_sqlite3.sql /app/
RUN find /app/ -name ".*" -maxdepth 1 -exec rm -rf {} \; && \
	sed -i 's/host = "localhost"/host = "0.0.0.0"/g' config.toml && \
	sed -i 's/port = 8080/port = 80/g' config.toml && \
	python3 /tmp/db-init/init_sqlite3.py && \
	rm -r /tmp/db-init

ARG VERSION
ENV VERSION=$VERSION
CMD /usr/local/bin/python3 -u ./run.py
EXPOSE 80
