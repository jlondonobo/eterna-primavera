FROM python:3.9

ARG ACCESS_TOKEN
ARG GITHUB_USER
RUN pip install human@git+https://${GITHUB_USER}:${ACCESS_TOKEN}@github.com/HumanLD/human-tools
RUN pip install real_estate@git+https://${GITHUB_USER}:${ACCESS_TOKEN}@github.com/HumanLD/human-real-estate --no-deps

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . app/
WORKDIR app

CMD streamlit run app.py --server.port 80