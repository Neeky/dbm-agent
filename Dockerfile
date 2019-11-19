FROM 1721900707/dbma:0.0.1.0
#FROM centos:7.6.1810



MAINTAINER neeky@live.com
#QQ:1721900707
#WeChat: jianglegege
#ENV PYTHON_VERSION 3.6.0
#ENV PATH /usr/local/python/bin/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#ENV LANG zh_CN.UTF-8
#
#
#WORKDIR /tmp/
#
#RUN set -ex \
#    && yum -y install gcc gcc-c++ libffi libyaml-devel libffi-devel zlib zlib-devel openssl shadow-utils \
#    openssl-devel libyaml sqlite-devel libxml2 libxslt-devel libxml2-devel wget vim mysql-devel \
#    && yum clean all 
#
#
#RUN set -ex \
#    && wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
#    && mkdir -p /usr/src/python \
#    && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
#    && rm python.tar.xz \
#    && cd /usr/src/python \
#    && ./configure \
#    --prefix=/usr/local/python-${PYTHON_VERSION%%[a-z]*}/ \
#    && make -j "$(nproc)" \
#    && make install \
#    && ldconfig \
#    && ln -s /usr/local/python-${PYTHON_VERSION%%[a-z]*} /usr/local/python \
#    && find /usr/local/python-${PYTHON_VERSION%%[a-z]*}/ -depth \
#    \( \
#    \( -type d -a \( -name test -o -name tests \) \) \
#    -o \
#    \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
#    \) -exec rm -rf '{}' + \
#    && rm -rf /usr/src/python \
#    && python3 --version 
#
#
#RUN pip3 install jinja2 psutil mysql-connector-python==8.0.18 requests distro --index-url  https://mirrors.aliyun.com/pypi/simple

ADD . /tmp/

CMD python3 --version