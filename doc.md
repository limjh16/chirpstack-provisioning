# DOC

- We want to use [`google.protobuf.json_format`](https://googleapis.dev/python/protobuf/latest/google/protobuf/json_format.html) module to parse the json data into protobuf messages
    - Hence, data files should follow the fields defined in the `proto` files
    - To validate / develop these data files, we generate `jsonschema` files based on these `proto` files using [`bufbuild/protoschema-plugins`](https://github.com/bufbuild/protoschema-plugins)
- However, this makes things messy since we would have to maintain a separate data file for each group (e.g., one for application, one for device, etc)
- The plan is to modify these schemas slightly, to allow embedding json objects in a tree format that we choose to define
    - Each individual object should still conform strictly to the required `proto` message, but we are basically just nesting messages together
    - Hopefully, we are able to do this by creating a very minimal schema file, which `$ref`s all of the auto-generated ones together, in the tree that we want
