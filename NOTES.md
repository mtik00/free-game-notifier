# Building Docker

Build the `latest` image with:

    make build

Build both `latest` and the versioned image with:

    make VERSION=$(poetry version -s) build

Push the `latest` image with:

    make push

Push both `latest` and the versioned image with:

    make VERSION=$(poetry version -s) push

# Bumping Version

    poetry version minor \
    && git add pyproject.toml \
    && git ci -m"bumping version" \
    && git tag v$(poetry version -s) \
    && git push && git push --tags \
    && make VERSION=$(poetry version -s) push