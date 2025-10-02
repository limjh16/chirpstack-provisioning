# the `golang` image is actually quite big, but refer to: https://github.com/docker-library/golang/issues/427#issuecomment-1863649891
# we only use it as a builder, and the files will run in a separate image later
# version is fixed for reproducability's sake, but the latest version should always work
ARG GO_VERSION="1"
ARG DEBIAN_VERSION="trixie"
FROM golang:${GO_VERSION}-${DEBIAN_VERSION} AS builder

# Same as above, version is locked just for reproducability's sake
# As an additional benefit, this layer of the `Dockerfile` is cached until the commit hash is explicitly change. No need to manually run without cache, each change of version should be explicit.
# Should check if there is a newer version, and test if it works if required
ARG COMMIT_HASH="a1fe39d"
RUN CGO_ENABLED=0 go install \
    github.com/bufbuild/protoschema-plugins/cmd/protoc-gen-jsonschema@${COMMIT_HASH}

# From best practices, https://docs.docker.com/build/building/best-practices/#run
# We do this instead of `apt-get install protobuf-compiler` since we need the binary to be a portable statically-linked binary
RUN apt-get update && apt-get install -y --no-install-recommends \
   unzip \
   && rm -rf /var/lib/apt/lists/*
WORKDIR /root/protobuf
ARG PB_REL="https://github.com/protocolbuffers/protobuf/releases"
ARG PB_VER="32.1"
RUN PB_ARCH=$(uname -m | sed s/arm64/aarch_64/ | sed s/aarch64/aarch_64/) && \
    curl -LO ${PB_REL}/download/v${PB_VER}/protoc-${PB_VER}-linux-$PB_ARCH.zip && \
    unzip protoc-${PB_VER}-linux-$PB_ARCH.zip -d /usr/


FROM scratch AS runner

# NOTE: `/go` should be $GOPATH, but this might change. Same as `/usr/bin`, which is apt's install directory for binaries.
COPY --from=builder /go/bin/protoc-gen-jsonschema /usr/bin/
COPY --from=builder /usr/bin/protoc /usr/bin/
COPY --from=builder /usr/include/google/protobuf /usr/include/google/protobuf

VOLUME /proto
WORKDIR /proto
ENTRYPOINT ["protoc"]

# NOTE: build with `docker build -t chirpstack-provisioning/protoc-gen-jsonschema .`
# run with `docker run --rm --mount type=bind,src=/src,dst=/proto chirpstack-provisioning/protoc-gen-jsonschema:latest` followed by all the other options
# For example:
#   docker run --rm --mount type=bind,src=.,dst=/proto chirpstack-provisioning/protoc-gen-jsonschema:latest \
#       --jsonschema_out=jsonschema/ --jsonschema_opt=target=json-strict api/device.proto
