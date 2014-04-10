import collections
import os
import shelve
from itertools import chain

class Multishelf(collections.MutableMapping):
    def __init__(self, db_dir, flag='c', protocol=None, writeback=False):
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self._shelves = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            self._shelves[letter] = shelve.open(os.path.join(db_dir, letter+'.db'),
                                             flag, protocol, writeback)
            
    def __getitem__(self, key):
        return self._shelves.get(key[0].lower(), self._shelves['#'])[key]
    
    def __setitem__(self, key, value):
        self._shelves.get(key[0].lower(), self._shelves['#'])[key] = value
    
    def __delitem__(self, key):
        del self._shelves.get(key[0].lower(), self._shelves['#'])[key]
    
    def __iter__(self):
        return chain(*(iter(d) for d in self._shelves.itervalues()))
    
    def __len__(self):
        return sum(len(d) for d in self._shelves.itervalues())
    
    def update(self, *args, **kwds):
        if len(args) == 1 and isinstance(args[0], Multishelf):
            # update backend shelve by backend shelve
            for letter in 'abcdefghijklmnopqrstuvwxyz1234567890#':
                self._shelves[letter].update(args[0]._shelves[letter])
            super(Multishelf, self).update(**kwds)
        else:
            super(Multishelf, self).update(*args, **kwds)
            
    def sync(self):
        for d in self._shelves.values():
            d.sync()
                        
    def close(self):
        for d in self._shelves.values():
            d.close()
            
def open(*args, **kwds):
    """Return a multishelf"""
    return Multishelf(*args, **kwds)