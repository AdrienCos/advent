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

init-day day:
    cp src/dayXX.py src/day{{ day }}.py
    sops edit inputs/day{{ day }}.txt.enc
    sops decrypt --output inputs/day{{ day }}.txt inputs/day{{ day }}.txt.enc
