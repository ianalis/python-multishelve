import collections
import os
import shelve
from itertools import chain

class Multishelf(collections.MutableMapping):
    def __init__(self, db_dir, flag='c', protocol=None, writeback=False):
        self.dicts = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            self.dicts[letter] = shelve.open(os.path.join(db_dir, letter+'.db'),
                                             flag, protocol, writeback)
            
    def __getitem__(self, key):
        return self.dicts.get(key[0].lower(), self.dicts['#'])[key]
    
    def __setitem__(self, key, value):
        self.dicts.get(key[0].lower(), self.dicts['#'])[key] = value
    
    def __delitem__(self, key):
        del self.dicts.get(key[0].lower(), self.dicts['#'])[key]
    
    def __iter__(self):
        return chain(*(iter(d) for d in self.dicts.itervalues()))
    
    def __len__(self):
        return sum(len(d) for d in self.dicts.itervalues())
    
    def sync(self):
        for d in self.dicts.values():
            d.sync()
                        
    def close(self):
        for d in self.dicts.values():
            d.close()