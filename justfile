default:
    @echo "Usage: just <recipe>"
    @echo ""
    @echo "Recipes:"
    @echo "  build    - Build Podman image novasr-cpu:latest"
    @echo "  rebuild  - Force rebuild Podman image"
    @echo "  run      - Run container interactively"
    @echo "  clean    - Remove Podman image"

build:
    podman build -t novasr-cpu:latest .

rebuild:
    podman build --no-cache -t novasr-cpu:latest .

run:
    podman run -it --rm -v "$(pwd)":/app/data novasr-cpu:latest

clean:
    podman rmi novasr-cpu:latest
