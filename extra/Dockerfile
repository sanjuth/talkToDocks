FROM public.ecr.aws/lambda/python:3.9


COPY requirements.txt ./
# RUN pip3 install --no-cache-dir  -r requirements.txt 
RUN pip3 install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host github.com -r requirements.txt
# RUN python3 -m spacy download en_core_web_sm  && \
#     python3 -m spacy download en 

COPY talk-docs.py ./ 

CMD [ "talk-docs.lambda_handler" ] #replace you scrip name with sci.py