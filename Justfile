install:
    uv sync --all-extras --dev

install-tuna:
    uv sync --all-extras --dev --index-url https://pypi.tuna.tsinghua.edu.cn/simple

ruff:
    uvx ruff check . --fix --unsafe-fixes
    uvx ruff format .

ty:
    uvx ty check

test:
    uv run pytest --cov=nanoflow --codspeed --xdoc
    uv run coverage xml

check:
    just ruff
    just ty

push:
    just test
    git push
    git push --tags
