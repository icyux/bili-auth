FROM python:3.11.5-bullseye AS env-build
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

FROM python:3.11.5-slim-bullseye
COPY --from=env-build /usr/local/bin/ /usr/local/bin/
COPY --from=env-build /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=env-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
RUN rm /etc/apt/sources.list; \
	echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free' >> /etc/apt/sources.list; \
	echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free' >> /etc/apt/sources.list; \
	echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free' >> /etc/apt/sources.list; \
	echo 'deb https://security.debian.org/debian-security buster/updates main contrib non-free' >> /etc/apt/sources.list;
RUN apt update && apt install -y chromium chromium-driver
WORKDIR /app/
COPY ./ /app/
RUN sed -i 's#browserPath = ""#browserPath = "/usr/bin/chromium"#g' config.toml; \
	sed -i 's/# "--no-sandbox"/"--no-sandbox"/g' config.toml; \
	sed -i 's/localhost:8080/0.0.0.0:8080/g' uwsgi.ini;
RUN python3 init_sqlite3.py

CMD /usr/local/bin/uwsgi --ini uwsgi.ini
EXPOSE 8080
