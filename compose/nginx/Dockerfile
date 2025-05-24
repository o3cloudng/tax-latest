FROM nginx:1.25-alpine

RUN apk add --no-cache openssl && \
    rm -rf /etc/nginx/conf.d/* && \
    mkdir -p /var/www/certbot

COPY ./compose/production/nginx/conf /etc/nginx/conf.d
COPY ./compose/production/nginx/ssl /etc/letsencrypt

RUN chown -R nginx:nginx /var/www/certbot && \
    chmod -R 755 /var/www/certbot