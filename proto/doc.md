# Documentation for generation

CURRENT CHIRPSTACK API COMMIT: [`03f87e7`](https://github.com/chirpstack/chirpstack/tree/03f87e73ddc56504292a5f2b34652cb6a065a1e2/api/proto)

- [`bufbuild/protoschema-plugins`](https://github.com/bufbuild/protoschema-plugins) was used since it generates `jsonschema` files for the latest schema.
    - Originally wanted to use [`chrusty/protoc-gen-jsonschema`](https://github.com/chrusty/protoc-gen-jsonschema), but found that there was a "newer version" from the issues (https://github.com/chrusty/protoc-gen-jsonschema/issues/100#issuecomment-1995795515)
        - Wanted the newer schema version so that we can use JSON pointers to reference other subschemas
    - It also seems that the [`bufbuild/protovalidate`](https://github.com/bufbuild/protovalidate) is a solid and popular choice for validating `protobuf` messages, might be able to use it in the future
    - A `Dockerfile` is included that runs `protoc` together with the `jsonschema` plugin if you do not want to install `go` and other dependencies on the machine. Instructions are in the `Dockerfile` itself.
        - Honestly, this was quite dumb since `bufbuild/protoschema-plugins` doesn't distribute compiled binaries. If I have some time I might just make a github action within this repository to generate and distribute a binary for them
        - Maybe a github action that tracks changes to `chirpstack` and the `.proto` API files??
- For the purposes of `chirpstack-provisioning`, we generate these `jsonschema` files with `--jsonschema_opt=target=json-strict`

## Command ran to generate the `jsonschema` files

- Download the entire `api/proto` directory from <download-directory.github.io?url=https://github.com/chirpstack/chirpstack/tree/03f87e73ddc56504292a5f2b34652cb6a065a1e2/api/proto>
- Extract the `api`, `google`, and `common` folders into this folder
- The resultant directory structure should look like:

```
proto (this current folder)/
├─ api/
│  ├─ ...proto
├─ common/
│  ├─ common.proto
├─ Dockerfile
├─ jsonschema/
│  ├─ .../
├─ google/api/
│  ├─ annotations.proto
│  ├─ http.proto
```

- After that, the short bash for-loop below can be ran to generate the `jsonschema` files.
    - NOTE: `protoc` can be replaced with `docker run ...`

```sh
for f in api/*.proto; do
    fname="$(basename $f .proto)"
    mkdir -p jsonschema/$fname
    protoc --jsonschema_opt=target=json-strict --jsonschema_out=jsonschema/$fname api/$fname.proto
done
```

## Schema Bundling

The `bundler/` directory contains a TypeScript utility that bundles `setup.schema.json` and all its dependencies from `jsonschema/` into a single `bundled.schema.json` file using [`@hyperjump/json-schema`](https://github.com/hyperjump-io/json-schema).

To run the bundler:

```bash
cd proto/bundler
npm install  # First time only
npm run bundle
```

This creates a self-contained `bundled.schema.json` in the repository root with all external schema references embedded in the `$defs` section.

See [bundler/README.md](bundler/README.md) for more details.

## Other things tried
- The [`pubg/protoc-gen-jsonschema`](https://github.com/pubg/protoc-gen-jsonschema) behaved kinda weirdly, honestly forgot what specific problem I had but it didn't fit the needs
