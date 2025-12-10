# ========================================
# Apache2 (httpd) Dockerfile for NUAM
# ========================================
# This container acts as the primary reverse proxy layer
# in front of Nginx, providing:
# - HTTPS/SSL termination
# - ProxyPass to Nginx backend
# - Rate limiting
# - Security headers
# ========================================

FROM httpd:2.4-alpine

# Install required modules
RUN apk add --no-cache \
    apache2-proxy \
    apache2-ssl \
    openssl

# Enable required Apache modules
RUN sed -i \
    -e 's/^#\(LoadModule .*mod_proxy.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_proxy_http.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_proxy_balancer.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_ssl.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_socache_shmcb.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_rewrite.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_headers.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_deflate.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_filter.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_expires.so\)/\1/' \
    -e 's/^#\(LoadModule .*mod_ext_filter.so\)/\1/' \
    /usr/local/apache2/conf/httpd.conf

# Copy custom configuration
COPY httpd.conf /usr/local/apache2/conf/httpd.conf
COPY conf.d/ /usr/local/apache2/conf/conf.d/

# Create directory for SSL certificates
RUN mkdir -p /usr/local/apache2/conf/ssl

# Expose HTTP and HTTPS ports
EXPOSE 80 443

# Start Apache in foreground
CMD ["httpd-foreground"]
