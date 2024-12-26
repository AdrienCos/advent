set positional-arguments := true
default_year := '2024'

run day year=default_year:
    sops exec-file inputs/{{ year }}/day{{ day }}.txt.enc "./venv/bin/python src/{{ year }}/day{{ day }}.py {}"

time day year=default_year:
    sops exec-file --no-fifo inputs/{{ year }}/day{{ day }}.txt.enc "hyperfine \"./venv/bin/python src/{{ year }}/day{{ day }}.py {}\""

show-input day year=default_year:
    sops decrypt inputs/{{ year }}/day{{ day }}.txt.enc

install:
    virtualenv -p python3 venv
    ./venv/bin/pip install -r requirements.txt

init-day day year=default_year:
    cp src/dayXX.py src/{{ year }}/day{{ day }}.py
    sops edit inputs/{{ year }}/day{{ day }}.txt.enc
    sops decrypt --output inputs/{{ year }}/day{{ day }}.txt inputs/{{ year }}/day{{ day }}.txt.enc
