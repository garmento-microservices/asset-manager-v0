ARG PYTHON_BASE=3.11-slim
# Base Image (with base APT packages)
FROM python:$PYTHON_BASE AS base

# install required dependencies
RUN apt update && apt upgrade -y

# build stage
FROM base AS builder

# install PDM
RUN pip install -U pdm
# disable update check
ENV PDM_CHECK_UPDATE=false
# copy files
COPY pyproject.toml README.md /project/

# install dependencies and project into the local packages directory
WORKDIR /project
RUN pdm install --frozen-lockfile --prod --no-editable --no-isolation --no-self
COPY src/ /project/src

# run stage
FROM base

# retrieve packages from build stage
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"
# set command/entrypoint, adapt to fit your needs
COPY src /project/src
COPY .env /project/
WORKDIR /project
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "src", "--env-file", ".env", "--host", "0.0.0.0"]
