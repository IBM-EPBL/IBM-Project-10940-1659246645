FROM helloworld:latest 
WORKDIR ~/Desktop/ 
ADD . helloworld/
WORKDIR ~/Desktop/htmlfile 
RUN pip install -r requirements 
RUN chmod +x app.sh
CMD ["/bi n/sh","app.sh"]
