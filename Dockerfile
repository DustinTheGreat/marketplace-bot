FROM python:3.7.2-alpine3.9

## Adding Packages for AI and staticial analysis###


RUN apk add --no-cache python3-dev libstdc++ && \
    apk add --no-cache g++ && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install numpy && \
    pip3 install pandas


RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip3 install Pillow


## Geting everything ready to install Selenium

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.4/main" >> /etc/apk/repositories && \
	echo "http://dl-4.alpinelinux.org/alpine/v3.4/community" >> /etc/apk/repositories


RUN apk update && \
	apk add curl unzip libexif udev chromium chromium-chromedriver xvfb && \
	pip3 install selenium && \
	pip3 install pyvirtualdisplay



#########################
#########################
# DEFINE ENV VARS HERE
# ENV username=test
#     password=12345
#########################
#########################
ENV USERNAME=email

ENV PASSWORD=pass


COPY requirements.txt .

RUN pip3 install -r requirements.txt
# Install the chromium browser and driver
RUN apk update

# set display port to avoid crash
ENV DISPLAY=:99

# Clean up disk space
RUN rm -Rf ~/.cache

COPY . .

RUN chmod 777 main.py

CMD ["python", "main.py"]
