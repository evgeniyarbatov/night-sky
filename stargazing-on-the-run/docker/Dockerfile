FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    stellarium \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Bake a default config.ini and disable the online-catalog plugins (satellites,
# exoplanets, novae, meteor showers): they retry network updates on every
# startup and stall a network-less/offline container indefinitely.
RUN Xvfb :99 -screen 0 1280x800x24 & \
    sleep 1 && \
    DISPLAY=:99 timeout 5 stellarium || true; \
    sed -i \
      -e 's/^\(Exoplanets *\)= true/\1= false/' \
      -e 's/^\(Novae *\)= true/\1= false/' \
      -e 's/^\(Satellites *\)= true/\1= false/' \
      -e 's/^\(MeteorShowers *\)= true/\1= false/' \
      -e 's/^updates_enabled *= true/updates_enabled                        = false/' \
      -e 's/^automatic_updates_enabled *= true/automatic_updates_enabled              = false/' \
      -e 's/^flag_script_allow_write_absolute_path *= false/flag_script_allow_write_absolute_path  = true/' \
      -e '/^\[scripts\]/a flag_allow_screenshots_dir             = true' \
      /root/.stellarium/config.ini

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
