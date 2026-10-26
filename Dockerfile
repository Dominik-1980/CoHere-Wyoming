FROM python:3.11-slim-bookworm
ARG VERSION=0.1.0
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="CoHere-Wyoming" \
      org.opencontainers.image.description="Local Cohere Transcribe speech recognition over Wyoming" \
      org.opencontainers.image.source="https://github.com/Dominik-1980/CoHere-Wyoming" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      net.unraid.docker.icon="https://raw.githubusercontent.com/Dominik-1980/CoHere-Wyoming/main/assets/logo.png" \
      net.unraid.docker.webui="http://[IP]:[PORT:10301]/docs"
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/data/hf \
    HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 NUMBA_CACHE_DIR=/data/numba \
    OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 LANGUAGE=de MODEL_DIR=/data/model \
    MODEL_DOWNLOAD=1 HF_TOKEN_PATH=/run/secrets/hf_token HOME=/data
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.11.0 \
    && pip install -r requirements.txt
COPY patch_backend.py prepare_model.py healthcheck.py entrypoint.sh model-manifest.json LICENSE NOTICE THIRD_PARTY.md /app/
COPY licenses /app/licenses
COPY assets /app/assets
COPY scripts /app/scripts
RUN python /app/patch_backend.py && chmod +x /app/entrypoint.sh \
    && python /app/scripts/export_licenses.py \
    && mkdir -p /data && chown 1000:1000 /data
USER 1000:1000
EXPOSE 10300 10301
HEALTHCHECK --interval=30s --timeout=5s --start-period=1800s --retries=3 CMD ["python", "/app/healthcheck.py"]
ENTRYPOINT ["/app/entrypoint.sh"]
