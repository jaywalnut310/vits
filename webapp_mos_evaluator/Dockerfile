# Stage 1: builder
FROM ubuntu:22.04 AS builder

WORKDIR /app/webapp_mos_evaluator

# set timezone:
ENV CONTAINER_TIMEZONE=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# setup pacakges
RUN apt-get update
RUN apt-get install -y curl build-essential pkg-config libssl-dev cmake python3 python3-pip
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"


# copy only the necessary files
COPY ./Cargo.toml ./Cargo.lock ./
COPY ./src ./src

ENV RUST_BACKTRACE=1
ENV RUST_LOG=info
ENV RUSTFLAGS="-D warnings"

RUN cargo check --verbose

# build binary
RUN cargo install --path .

# Stage 2: creating the runtime image
FROM ubuntu:22.04

ARG BUILD_DATE
RUN echo "$BUILD_DATE" > /build_date.txt

WORKDIR /app/webapp_mos_evaluator

# Set timezone
ENV CONTAINER_TIMEZONE=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
RUN apt-get update
RUN apt-get install -y curl lsb-release

# Copy the compiled binary from the build stage
COPY --from=builder /root/.cargo/bin/webapp_mos_evaluator /app/webapp_mos_evaluator
COPY ./static ./static

# Set the entrypoint and command
ENTRYPOINT [ "/app/webapp_mos_evaluator/webapp_mos_evaluator" ]
