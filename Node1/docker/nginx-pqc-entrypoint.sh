#!/usr/bin/env bash
set -e

OPENSSL_PREFIX="${OPENSSL_PREFIX:-/opt/src/openssl-3.5.0/.openssl}"
NGINX_PREFIX="${NGINX_PREFIX:-/opt/nginx-pqc}"
PQC_OPENSSL_CONF="${PQC_OPENSSL_CONF:-/opt/openssl-3.5/ssl/pqc-openssl.cnf}"

NGINX_BIN="$NGINX_PREFIX/sbin/nginx"

# Prefer custom bins/libs (also set by Dockerfile ENV, but keeping here is harmless)
export PATH="$NGINX_PREFIX/sbin:$OPENSSL_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$OPENSSL_PREFIX/lib64:$OPENSSL_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export OPENSSL_CONF="$PQC_OPENSSL_CONF"

echo "Using custom nginx and openssl:"
echo "  nginx   -> $(command -v nginx || echo 'not in PATH')"
echo "  openssl -> $(command -v openssl || echo 'not in PATH')"
echo "  OPENSSL_CONF -> $OPENSSL_CONF"
echo

echo "Stopping existing PQC nginx if running..."
if pgrep -f "$NGINX_BIN" >/dev/null 2>&1; then
  "$NGINX_BIN" -s quit || true
  sleep 1
fi

case "$1" in
  nginx)
    echo "Testing PQC nginx config..."
    "$NGINX_BIN" -t -c "$NGINX_PREFIX/conf/nginx.conf"

    echo "Starting PQC nginx in foreground (nginx-only mode)..."
    exec "$NGINX_BIN" -g "daemon off;" -c "$NGINX_PREFIX/conf/nginx.conf"
    ;;

  ./run_web_app.sh)
    echo "Starting web application backend: ./run_web_app.sh"
    /app/run_web_app.sh &

    echo "Testing PQC nginx config..."
    "$NGINX_BIN" -t -c "$NGINX_PREFIX/conf/nginx.conf"

    echo "Starting PQC nginx in foreground (frontend for the app)..."
    exec "$NGINX_BIN" -g "daemon off;" -c "$NGINX_PREFIX/conf/nginx.conf"
    ;;

  -*)
    echo "Testing PQC nginx config..."
    "$NGINX_BIN" -t -c "$NGINX_PREFIX/conf/nginx.conf"

    echo "Starting PQC nginx in foreground with custom options..."
    exec "$NGINX_BIN" "$@"
    ;;

  *)
    exec "$@"
    ;;
esac
