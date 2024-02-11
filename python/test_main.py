import os
import unittest
import shutil
from main import init_batch_dir, organize_files

class TestBatchDirectory(unittest.TestCase):

    def setUp(self):
        # 创建临时测试目录
        self.test_dir = 'test_batch_dir'
        self.init_batch()
    
    def tearDown(self):
        # shutil.rmtree(self.test_dir)
        pass
    
    def init_batch(self):
        # 创建测试文件
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        test_files = []
        test_files.extend([f'a_batch10_{i}.txt' for i in range(10)])
        test_files.extend([f'a_batch20_{i}.txt' for i in range(20)])
        test_files.extend([f'a_batch5_{i}.txt' for i in range(5)])
        test_files.extend([f'b_batch30_{i}.txt' for i in range(30)])
        test_files.extend([f'b_batch20_{i}.txt' for i in range(20)])
        test_files.extend([f'b_batch5_{i}.txt' for i in range(5)])
        for filename in test_files:
            with open(os.path.join(self.test_dir, filename), 'w+'):
                pass

    def test_organize_files(self):
        init_batch_dir(self.test_dir)
        organize_files(self.test_dir)

if __name__ == '__main__':
    unittest.main()
