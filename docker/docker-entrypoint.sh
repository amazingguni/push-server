#!/bin/bash
set -x

UVICORN_OPTS=${UVICORN_OPS}

uvicorn ${UVICORN_OPTS} src.app:create_app  --host 0.0.0.0
