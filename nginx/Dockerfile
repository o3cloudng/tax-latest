FROM nginx

COPY ./nginx_start.sh /nginx_start.sh

RUN chmod +x /nginx_start.sh

# RUN touch /etc/nginx/conf.d/default.conf

COPY ./default.conf /etc/nginx/default.conf

ENTRYPOINT [ "sh", "-c", "/nginx_start.sh"]