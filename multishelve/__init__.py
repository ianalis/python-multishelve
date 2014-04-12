import collections
import os
import shelve
import string
from hashlib import md5
from base64 import urlsafe_b64encode as b64encode
from itertools import chain

class Multishelf(collections.MutableMapping):
    letters = string.ascii_letters + string.digits + '-_'
    
    def __init__(self, db_dir, flag='c', protocol=None, writeback=False):
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self._shelves = {}
        for letter in self.letters:
            self._shelves[letter] = shelve.open(os.path.join(db_dir, letter+'.db'),
                                             flag, protocol, writeback)
            
    def __getitem__(self, key):
        return self._shelves[b64encode(md5(key).digest())[0]][key]
    
    def __setitem__(self, key, value):
        self._shelves[b64encode(md5(key).digest())[0]][key] = value
    
    def __delitem__(self, key):
        del self._shelves[b64encode(md5(key).digest())[0]][key]
    
    def __iter__(self):
        return chain(*(iter(d) for d in self._shelves.itervalues()))
    
    def __len__(self):
        return sum(len(d) for d in self._shelves.itervalues())
    
    def update(self, *args, **kwds):
        if len(args) == 1 and isinstance(args[0], Multishelf):
            # update backend shelve by backend shelve
            for letter in self.letters:
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