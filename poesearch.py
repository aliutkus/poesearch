"""
usage: poesearch [-h] [--url URL] [--name [NAME [NAME ...]]]
                 [--mods [MODS [MODS ...]]] [--league LEAGUE]
                 [--type [TYPE [TYPE ...]]] [--slots SLOTS] [--links LINKS]

Quick and dirty script to search items in POE public tabs.

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL of the JSON export for public tabs, default:
                        http://www.pathofexile.com/api/public-stash-tabs
  --name [NAME [NAME ...]]
                        name of the item, arbitrary string
  --mods [MODS [MODS ...]]
                        mods for the item, strings separated by comma
  --league LEAGUE       league to search items
  --type [TYPE [TYPE ...]]
                        type of the item, character string
  --slots SLOTS         number of slots for the item, integer
  --links LINKS         number of links for the item, integer

Example of use:
                    python poesearch.py --mods armour 1000, life 60 --slots 5 --links 3
                    python poesearch.py --type wand --mods critical strike chance 100
                    python poesearch.py --links 6
                    python poesearch.py --name the bringer of rain

                    --------------------
                    Antoine Liutkus 2016
"""
#imports
from urllib import urlopen
import json
import re
import pprint as pp
import argparse
import sys


default_url = 'http://www.pathofexile.com/api/public-stash-tabs'


def find_items(url=default_url, league = None, name=None, mods=None,type=None,slots=None,links=None):
    '''Find items in poe public tabs json file'''
    print 'Looking for items matching query...'

    #open the json file

    jsonurl = urlopen(url)
    dat = json.loads(jsonurl.read())

    #initialize results
    result = []

    #looping over stashes
    for stash in dat['stashes']:
        #looping over items
        for item in stash['items']:

            #league
            if league is not None and not re.search(league.upper(), item['league'].upper()):
                continue

            #name
            if name is not None and not re.search(name.upper(), item['name'].upper()):
                continue

            #type
            if type is not None and not re.search(type.upper(), item['typeLine'].upper()):
                continue

            #building the list of properties and mods of the item
            item_mods =  []
            for mod_field in ['explicitMods','implicitMods']:
                if item.has_key(mod_field): item_mods += item[mod_field]
            if item.has_key('properties'):
                for property in item['properties']:
                    if not len(property['values']):continue
                    item_mods += [property['name']+' '+str(property['values'][0][0]),]

            #filtering over mods if required
            if mods is not None:
                for mod in mods:
                    #for each mod required

                    keep = False

                    for item_mod in item_mods:
                        #looping over item mods
                        item_mod_matching = True

                        for mod_sub in re.findall(r"[\w']+", mod):
                            if mod_sub.isdigit():
                                numbers_item = re.findall(r'\d+', item_mod)
                                if not any([float(mod_sub) < float(x) for x in numbers_item]):
                                     item_mod_matching=False
                                     break
                            else:
                                if not re.search(mod_sub.upper(),item_mod.upper()):
                                    item_mod_matching=False
                                    break
                        keep = keep or item_mod_matching
                        if keep:break
                    if not keep: break
                if not keep: continue

            #number of sockets
            if slots is not None and len(item['sockets'])<slots:
                continue

            #linked sockets
            groupsize = [0,0,0,0,0,0]
            for socket in item['sockets']:
                groupsize[socket['group']]+=1
            nlink = max(groupsize)
            if nlink==0:
                socketString=None
            else:
                socketString='%dS%dL'%(len(item['sockets']),nlink)
            if links is not None:
                if nlink<links:
                    continue

            #found item

            result += [{'player':stash['accountName'],'item':item,'sockets':socketString ,'mods':item_mods}]

    print '\n\n%d items found.'%len(result)
    for res in result:
        print '---------------------'
        print 'seller :', res['player']
        if len(res['item']['name'])>27:
            print 'name   :',res['item']['name'][28:]
        print 'type   :',res['item']['typeLine']
        if res['sockets'] is not None:
            print 'sockets:',res['sockets']
        if res['item'].has_key('note'):
            print 'note   :',res['item']['note']
        print 'details:'
        pp.pprint(res['mods'])



if __name__ == "__main__":
    epilogString =  '''Example of use:
                    python poesearch.py --mods armour 1000, life 60 --slots 5 --links 3
                    python poesearch.py --type wand --mods critical strike chance 100
                    python poesearch.py --links 6
                    python poesearch.py --name the bringer of rain


                    --------------------
                    Antoine Liutkus 2016'''

    import textwrap
    parser = argparse.ArgumentParser(prog='poesearch',description='Quick and dirty script to search items in POE public tabs.',formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent(epilogString))
    parser.add_argument('--url',nargs=1,type=str, default=default_url,help='URL of the JSON export for public tabs, default: '+default_url )
    parser.add_argument('--name', nargs='*',default=None,help='name of the item, arbitrary string')
    parser.add_argument('--mods', nargs='*',default = None, type=str,help='mods for the item, strings separated by comma')
    parser.add_argument('--league', nargs=1,default=None, help='league to search items')
    parser.add_argument('--type', nargs='*',default=None,help='type of the item, character string')
    parser.add_argument('--slots',nargs=1,type=int, default=None,help='number of slots for the item, integer')
    parser.add_argument('--links',nargs=1,type=int, default=None,help='number of links for the item, integer' )


    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)


    if args.name is not None:  args.name= ' '.join(args.name)
    if args.mods is not None:  args.mods= ' '.join(args.mods).split(',')
    if args.type is not None:  args.type= ' '.join(args.type)
    if args.slots is not None:args.slots = args.slots[0]
    if args.links is not None:args.links = args.links[0]

    find_items(url=args.url,league = args.league, name=args.name, mods=args.mods,type=args.type,slots=args.slots,links=args.links)
