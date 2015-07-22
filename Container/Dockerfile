FROM gliderlabs/alpine
RUN apk-install python python-dev py-pip build-base
ADD requirements.txt /
ADD ./github_status.py /
RUN pip install -U pip && pip install -r requirements.txt
ENV GITHUB_TOKEN=*your-github-token*
CMD python github_status.py