from pathlib import Path
import json
import dataflows as DF


if __name__ == '__main__':
    for f_in in Path().glob('src/datasets/*json'):
        if 'datapackage' in str(f_in):
            continue
        resources, dp, _ = DF.Flow(
            DF.load(str(f_in)),
            DF.delete_fields(['created_at', 'updated_at', 'id'])
        ).results()
        del dp.descriptor['resources'][0]['path']
        dp.descriptor['resources'][0]['data'] = resources[0]
        dp.commit()
        json.dump(dp.descriptor, f_in.with_suffix('.datapackage.json').open('w'), indent=2, ensure_ascii=False, sort_keys=True)