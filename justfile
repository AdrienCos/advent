run day:
    sops exec-file inputs/day{{ day }}.txt.enc "./venv/bin/python src/day{{ day }}.py {}"

time day:
    sops exec-file --no-fifo inputs/day{{ day }}.txt.enc "hyperfine \"./venv/bin/python src/day{{ day }}.py {}\""

benchmark day:
    sops exec-file --no-fifo inputs/day{{ day }}.txt.enc "poop \"./venv/bin/python src/day{{ day }}.py {}\""

show-input day:
    sops decrypt inputs/day{{ day }}.txt.enc

install:
    virtualenv -p python3 venv
    ./venv/bin/pip install -r requirements.txt
