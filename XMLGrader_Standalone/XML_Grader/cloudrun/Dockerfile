# 從 XML_Grader 目錄建立映像：docker build -f cloudrun/Dockerfile .
FROM python:3.11-slim
WORKDIR /app
COPY cloudrun/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY xml_grader_core.py api_server.py ./
ENV XMLGRADER_CONFIG_PATH=/tmp/xmlgrader/grader_config.json
ENV PORT=8080
CMD exec gunicorn -b 0.0.0.0:$PORT -w 1 --threads 8 --timeout 180 api_server:app
