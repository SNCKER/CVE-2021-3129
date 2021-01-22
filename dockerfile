FROM php:7.3.25-alpine

COPY laravel /src

WORKDIR /src

RUN cp .env.example .env \
	&& php -r "copy('https://install.phpcomposer.com/installer', 'composer-setup.php');" \
	&& php composer-setup.php \
	&& php -r "unlink('composer-setup.php');" \
	&& mv composer.phar /usr/local/bin/composer \
	&& chmod +x /usr/local/bin/composer \
	&& composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/ \
	&& composer install \
	&& composer require facade/ignition==2.5.1 \
	&& mv /usr/local/etc/php/php.ini-production /usr/local/etc/php/php.ini \
	&& sed -i 's/;phar.readonly = On/phar.readonly = 0/g' /usr/local/etc/php/php.ini


EXPOSE 8000

ENTRYPOINT ["php", "artisan", "serve", "--host=0.0.0.0"]

