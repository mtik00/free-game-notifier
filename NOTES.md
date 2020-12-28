# Building Docker

Build the `latest` image with:

    make build

Build both `latest` and the versioned image with:

    make VERSION=$(poetry version -s) build

Push the `latest` image with:

    make push

Push both `latest` and the versioned image with:

    make VERSION=$(poetry version -s) push
