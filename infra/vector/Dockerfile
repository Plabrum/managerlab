FROM timberio/vector:0.41-alpine

# Copy Vector configuration
COPY vector.yaml /etc/vector/vector.yaml

# Vector will read from stdin and forward to Betterstack
CMD ["--config", "/etc/vector/vector.yaml"]
