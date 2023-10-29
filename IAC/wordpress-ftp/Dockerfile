# Use an official PHP with Apache base image
FROM php:7.4-apache

# Set the working directory to /var/www/html
WORKDIR /var/www/html

# Copy the contents of the current directory into the container at /var/www/html
COPY . .

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y \
        libjpeg-dev \
        libpng-dev \
        libzip-dev \
        unzip \
        wget \
        proftpd \
    && rm -rf /var/lib/apt/lists/*

# Enable necessary Apache modules
RUN a2enmod rewrite

# Install PHP extensions
RUN docker-php-ext-configure gd --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
        gd \
        mysqli \
        opcache \
        zip

# Download and install WordPress
RUN wget -O wordpress.tar.gz https://wordpress.org/latest.tar.gz \
    && tar -xzf wordpress.tar.gz --strip-components=1 \
    && rm wordpress.tar.gz \
    && chown -R www-data:www-data .

# Set up a custom Apache configuration
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Add FTP user and password
RUN useradd -m -p $(openssl passwd -1 ftppassword) ftpuser

# Configure ProFTPD
COPY proftpd.conf /etc/proftpd/proftpd.conf

# Expose ports 20, 21, and 21100-21110 for FTP
EXPOSE 20 21 21100-21110

# Start Apache and ProFTPD servers
CMD service proftpd start && apache2-foreground
