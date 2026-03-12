FROM php:8.2-apache

# Habilitar mod_rewrite
RUN a2enmod rewrite

# Copiar archivos al directorio correcto
COPY . /var/www/html/

# Establecer permisos
RUN chmod -R 755 /var/www/html/
