import os
from pathlib import Path
from hashlib import md5
from slugify import slugify
import glob
import yaml
import json
import requests

def calc_hash(s):
    ret = md5(s.encode('utf8')).hexdigest()[:10]
    return ret


def get_field(x, f):
    parts = f.split('.')
    while len(parts) > 0:
        p = parts.pop(0)
        x = x.get(p, {})
    return x


def get_uid(x, stack, index=None):
    FIELDS = ['name', 'wait.variable', 'say', 'switch.arg', 'do.cmd', 'do.variable', 'match', 'pattern', 'default', 'show']
    values = [get_field(x, f) for f in FIELDS]
    values = ','.join([str(v) for v in values if v is not None])
    assert len(values) > 0
    current_hash = ''.join(stack)
    key = '{}|{}|{}'.format(current_hash, values, index)
    ret = calc_hash(key)
    return ret


def assign_ids(x, stack=[]):
    if isinstance(x, dict):
        uid = None
        for k, v in x.items():
            if k == 'steps':
                uid = get_uid(x, stack)
                for i, s in enumerate(v):
                    new_stack = stack + [uid, str(i)]
                    s['uid'] = get_uid(s, new_stack, i)
                    assign_ids(s, new_stack)    
            else:
                assign_ids(v, stack)
        if uid is not None:
            x['uid'] = uid
    elif isinstance(x, list):
        for xx in x:
            assign_ids(xx, stack)
    else:
        return

TRANSIFEX_TOKEN = os.environ.get('TRANSIFEX_TOKEN')
LANGUAGES = ('ar', 'am', 'en', 'ru')

def assign_translations(x, stack, lang=None, translations=None):
    if isinstance(x, dict):
        key = None
        if x.get('name'):
            stack.append(slugify(x['name']))
        if 'uid' in x:
            stack.append(x['uid'][:2])
        for k, v in x.items():
            if k == 'steps':
                for index, s in enumerate(v):
                    new_stack = stack + []
                    yield from assign_translations(s, new_stack, lang, translations)
            elif k in ('say', 'show'):
                key = '/'.join(str(s) for s in stack)
                yield key, v
            else:
                yield from assign_translations(v, stack[:], lang, translations)
        if lang is not None and key in translations:
            x.setdefault('.tx', {})[lang] = translations[key]
    elif isinstance(x, list):
        for index, xx in enumerate(x):
            new_stack = stack + [index]
            yield from assign_translations(xx, new_stack, lang, translations)


def transifex_session():
    s = requests.Session()
    s.auth = ('api', TRANSIFEX_TOKEN)
    return s


def transifex_slug(filename):
    return '_'.join(filename.parts).replace('.', '_')


def push_translations(filename: Path, translations):
    translations = dict(he=translations)
    content = yaml.dump(translations, allow_unicode=True, indent=2, width=1000000)

    slug = transifex_slug(filename)
    s = transifex_session()
    resp = s.get(f'https://www.transifex.com/api/2/project/equalityorgil/resource/{slug}/')

    if resp.status_code == requests.codes.ok:
        print('Update file:')
        data = dict(
            content=content,
        )

        resp = s.put(
            f'https://www.transifex.com/api/2/project/equalityorgil/resource/{slug}/content/',
            json=data
        )
        print(resp.status_code, resp.content[:50])
        
    else:
        print('New file:', slug)
        data = dict(
            slug=slug,
            name=str(filename),
            accept_translations=True,
            i18n_type='YAML_GENERIC',
            content=content,
        )

        resp = s.post(
            'https://www.transifex.com/api/2/project/equalityorgil/resources/',
            json=data
        ) 
        print(resp.status_code, resp.content[:50])


def pull_translations(lang, filename):
    s = transifex_session()
    slug = transifex_slug(filename)
    translations = s.get(
            f'https://www.transifex.com/api/2/project/equalityorgil/resource/{slug}/translation/{lang}/',
    ).json()
    translations = yaml.load(translations['content'], Loader=yaml.BaseLoader)['he']
    translations = dict((k, v) for k, v in translations.items() if v)
    return translations


if __name__=='__main__':
    for kind in ('user', 'agent'):
        print(kind)
        url_in = f'https://firestore.googleapis.com/v1/projects/reportit-script-builder/databases/(default)/documents/script/{kind}'
        f_in = Path(f'src/{kind}/script.yaml')
        content = requests.get(url_in).json()['fields']['yaml']['stringValue']
        scripts = yaml.load(content)
        yaml.dump(scripts, f_in.open('w'), allow_unicode=True, indent=2, width=1000000)
        assign_ids(scripts, [str(f_in)])

        if TRANSIFEX_TOKEN:
            translations = {}
            for script in scripts:
                for k, v in assign_translations(script, []):
                    assert k not in translations
                    translations[k] = v
            push_translations(f_in, translations)
            for lang in LANGUAGES: 
                translations = pull_translations(lang, f_in)
                for script in scripts:
                    for k, v in assign_translations(script, [], lang, translations):
                        pass

        scripts = dict(s=scripts)
        f_out = f_in.with_suffix('.json')
        json.dump(scripts, f_out.open('w'), ensure_ascii=False, sort_keys=True)
