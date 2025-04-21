# 
FROM python:3.9

# 
WORKDIR /code

ARG SEARCH_API_CODE_PATH
# 
COPY ${SEARCH_API_CODE_PATH}/requirements.txt /code/requirements.txt

# RUN pip install --upgrade pip

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install fastapi[standard]

# 
#COPY ./app /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "80"]