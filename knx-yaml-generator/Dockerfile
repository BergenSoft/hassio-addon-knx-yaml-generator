ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
      python3 \
      py3-yaml \
    && python3 --version

    
# Copy root filesystem
COPY rootfs /

# Labels
LABEL \
  io.hass.name="${BUILD_NAME}" \
  io.hass.type="addon" \
  io.hass.arch="${BUILD_ARCH}"
  
# Copy data for add-on
RUN chmod a+x /run.py


CMD [ "/run.py" ]
