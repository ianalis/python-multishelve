import unittest
import os
import shutil
import tempfile
import shelve
import random
import mox
import multishelve

class MultishelveTest(mox.MoxTestBase):
    def setUp(self):
        super(MultishelveTest, self).setUp()
        self.db_dir = tempfile.mkdtemp()
        self.db = multishelve.Multishelf(self.db_dir)
        self.expected = {}
        for k in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            self.expected[k] = self.db[k] = random.randint(0, 10000)

    def tearDown(self):
        if os.path.exists(self.db_dir):
            shutil.rmtree(self.db_dir)
     
    def test_new(self):
        """"Opening a nonexistent multishelve should create backend shelves"""
        self.db.close()
        shutil.rmtree(self.db_dir)
        self.db = multishelve.Multishelf(self.db_dir)
        
        for letter in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            self.assertTrue(os.path.exists(os.path.join(self.db_dir, 
                                                        letter+'.db')))
            
    def test_flag(self):
        """Flag type should be passed on to backend shelves"""
        self.db.close()
        
        self.mox.StubOutWithMock(shelve, 'open')
        for _ in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            shelve.open(mox.IgnoreArg(), 'r', mox.IgnoreArg(), mox.IgnoreArg())
            
        self.mox.ReplayAll()
        
        multishelve.Multishelf(self.db_dir, 'r')
        
    def test_protocol(self):
        """Protocol type should be passed on to backend shelves"""
        self.db.close()
        
        self.mox.StubOutWithMock(shelve, 'open')
        for _ in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            shelve.open(mox.IgnoreArg(), mox.IgnoreArg(), 2, mox.IgnoreArg())
            
        self.mox.ReplayAll()
        
        multishelve.Multishelf(self.db_dir, 'r', protocol=2)
        
    
    def test_writeback(self):
        """Writeback should be passed on to backend shelves"""
        self.db.close()
        
        self.mox.StubOutWithMock(shelve, 'open')
        for _ in 'abcdefghijklmnopqrstuvwxyz1234567890#':
            shelve.open(mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg(), True)
            
        self.mox.ReplayAll()
        
        multishelve.Multishelf(self.db_dir, writeback=True)
        
    def test_set(self):
        """Values must be placed in the appropriate backend shelve"""
        self.db.close()
        for k in self.expected:
            db = shelve.open(os.path.join(self.db_dir, k+'.db'), flag='r')
            self.assertEqual(db[k], self.expected[k])
            
    def test_get(self):
        """All set items must be retrieved by indexing"""
        for k,v in self.expected.items():
            self.assertEqual(self.db[k], v)
            
    def test_set_get_close(self):
        """Changes should persist"""
        self.db.close()
        self.db = multishelve.Multishelf(self.db_dir)
        self.test_get()
        
    def test_iter(self):
        """iter() should iterate over all backend dicts"""
        i = iter(self.db)
        self.assertNotIsInstance(i, list)
        self.assertItemsEqual(self.expected.keys(), list(i))
            
    def test_iterkeys(self):
        """iterkeys() should return an iterator over all backend dicts keys"""
        i = iter(self.db.iterkeys())
        self.assertNotIsInstance(i, list)
        self.assertItemsEqual(self.expected.keys(), list(i))
        
    def test_itervalues(self):
        """itervalues() should return an iterator over backend dicts values"""
        i = iter(self.db.itervalues())
        self.assertNotIsInstance(i, list)
        self.assertItemsEqual(self.expected.values(), list(i))
        
    def test_iteritems(self):
        """iteritems() should return an iterator over backend dicts items"""       
        i = iter(self.db.iteritems())
        self.assertNotIsInstance(i, list)
        self.assertItemsEqual(self.expected.items(), list(i))
        
    def test_keys(self):
        """keys() should return a list of all backend dicts keys"""        
        self.assertItemsEqual(self.expected.keys(), self.db.keys())
        
    def test_values(self):
        """values() should return a list of all backend dicts values"""        
        self.assertItemsEqual(self.expected.values(), self.db.values())
                
    def test_items(self):
        """items() should return a list of all backend dicts items"""        
        self.assertItemsEqual(self.expected.items(), self.db.items())
        
    def test_del(self):
        """del should delete key from the appropriate backend shelve"""
        for k in ('a', 'e', 'g', '0', '9', '#'):
            del self.db[k]
            del self.expected[k]
            
        self.assertItemsEqual(self.expected.items(), self.db.items())
        
    def test_len(self):
        """len() should return number of items in all backed dicts"""
        self.assertEqual(len(self.expected), len(self.db))
        
    def test_update(self):
        """update() should work for ordinary dict"""
        dict2 = {}
        for k in 'abc1234':
            dict2[k] = random.randint(0, 10000)
        for _ in range(10):
            dict2[str(random.randint(0, 10000))] = random.randint(0, 10000)
        
        self.db.update(dict2)
        self.expected.update(dict2)
        self.assertItemsEqual(self.expected.items(), self.db.items())
        
    def test_update_multishelve(self):
        """update() should work for multishelve"""
        db2_dir = tempfile.mkdtemp()
        db2 = multishelve.Multishelf(db2_dir)
        self.addCleanup(lambda: shutil.rmtree(db2_dir))
        dict2 = {}
        for k in 'abc1234':
            dict2[k] = db2[k] = random.randint(0, 10000)
        for _ in range(10):
            k = str(random.randint(0, 10000))
            dict2[k] = db2[k] = random.randint(0, 10000)
        
        self.maxDiff = None
        self.db.update(db2)
        self.expected.update(dict2)
        self.assertItemsEqual(self.expected.items(), self.db.items())
        
    def test_sync(self):
        """Syncing the multishelve must sync all backend shelves"""
        for key in self.db.dicts:
            self.db.dicts[key] = self.mox.CreateMockAnything()
        for d in self.db.dicts.values():
            d.sync()
            
        self.mox.ReplayAll()
        
        self.db.sync()
        
    def test_close(self):
        """Closing the multishelve must close all backend shelves"""
        for key in self.db.dicts:
            self.db.dicts[key] = self.mox.CreateMockAnything()
        for d in self.db.dicts.values():
            d.close()
            
        self.mox.ReplayAll()
        
        self.db.close()
        
        
if __name__ == "__main__":
    unittest.main()