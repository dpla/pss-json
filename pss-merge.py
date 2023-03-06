# Expects command line arg to directory containing all sets
# 
# python3 pss-merge.py /user/pss/sets
# 
# Where ./sets/ contains
#   ./sets/{set}/set.json
#   ./sets/{set}/items/{item_x}.json
#   ./sets/{set}/guide.json

import json
import os
import sys

base_path = sys.argv[1]
print(base_path)

for dirs in os.listdir(base_path):
    pss_set = dirs
    pss_dir = os.path.join(base_path,dirs )
    if os.path.isfile(pss_dir):
        continue
    print(pss_dir)

    f = open(f"{pss_dir}/set.json")
    j = json.load(f)

    replacement_items = list()

    # items 
    for s in [a for a in j['hasPart'] if 'disambiguatingDescription' in a and a['disambiguatingDescription']=='source']: 
        full_id = s['@id']
        id = full_id.split('/')[-1]
        item_file = f"{pss_dir}/items/{id}.json"
        item_f = open(item_file)
        item_j = json.load(item_f)

        item_j.pop('@context', None)
        s.update(item_j)

        replacement_items.append(s)
        item_f.close

    # Guide
    for g in [a for a in j['hasPart'] if 'disambiguatingDescription' in a and a['disambiguatingDescription']=='guide']: 
        guide_file = f"{pss_dir}/guide.json"
        guide_f = open(guide_file)
        guide_j = json.load(guide_f)

        guide_j.pop('@context', None)
        g.update(guide_j)

        replacement_items.append(g)
        guide_f.close

    # resources and overview 
    for t in [a for a in j['hasPart'] if a['name'] in ['Resources', 'Overview']]: 
        replacement_items.append(t)
    
    replacement = {'hasPart': replacement_items}
    j.update(replacement)
    f.close

    # Fix links 
    #   Find https://dp.la/primary-source-sets/sources/1734 (produces 404 w/o nginx redirects included in Beanstalk)
    #   Inject `second-ku-klux-klan-and-the-birth-of-a-nation` set name
    #   Result https://dp.la/primary-source-sets/second-ku-klux-klan-and-the-birth-of-a-nation/sources/1734/ (returns 200)
    s = json.dumps(j).replace('https://dp.la/primary-source-sets/sources/', f'https://dp.la/primary-source-sets/{pss_set}/sources/')
    j = json.loads(s)

    with open(f"{pss_dir}/updated_{pss_set}.json", "w") as o:
        json.dump(j, o, indent=3, sort_keys=True)
    o.close
