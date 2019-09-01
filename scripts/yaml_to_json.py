from pathlib import Path
import glob
import yaml
import json

if __name__=='__main__':
    files = Path().glob('src/*/script.yaml')
    for f_in in files:
        print(f_in)
        s = yaml.load(f_in.open())
        s = dict(s=s)
        f_out = f_in.with_suffix('.json')
        json.dump(s, f_out.open('w'), ensure_ascii=False, sort_keys=True)
