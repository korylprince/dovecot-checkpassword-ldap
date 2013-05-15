import unittest
import pickle
import subprocess
import os
from user import test_user

checkpassword = os.path.dirname(os.path.abspath(__file__))+'/checkpassword'
reply = os.path.dirname(os.path.abspath(__file__))+'/test-reply'

class TestCheckpassword(unittest.TestCase):

    def assertInEqual(self,a,b,val):
        """a in b and b[a] == val"""
        self.assertIn(a,b)
        self.assertEqual(b[a],val)

    def setUp(self):
        try:
            os.remove('/tmp/.checkpasswordenv.pickle')
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove('/tmp/.checkpasswordenv.pickle')
        except OSError:
            pass

    def fixEnv(self,env):
        for x in ['PYTHONHOME','VIRTUALENV','PATH']:
            if x in os.environ:
                env[x] = os.environ[x]

    def getChildEnv(self):
        with open('/tmp/.checkpasswordenv.pickle') as f:
            return pickle.load(f)

    def runChild(self,initenv,fail=False):
        self.fixEnv(initenv)

        in_fd,out_fd=os.pipe()
        os.write(out_fd,initenv['AUTH_USERNAME']+'\x00'+initenv['AUTH_PASSWORD']+'\x00')
        os.close(out_fd)

        p = subprocess.Popen([checkpassword,reply],env=initenv)
        p.wait()

        ret = p.returncode
        if fail:
            return ret

        if 'AUTHORIZED' in initenv:
            self.assertEqual(ret,2) #userdb
        else:
            self.assertEqual(ret,0) #passdb

        env = self.getChildEnv()

        for var in [x for x in test_user if x not in ['username','password','domain']]:
            self.assertInEqual(var,env,test_user[var])
        if 'AUTHORIZED' in initenv:
            self.assertInEqual('AUTHORIZED',env,'2')




    def testMasterValidNoDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'MASTER_USER': 'master', 'AUTH_USERNAME': test_user['username']}
        self.runChild(initenv)

    def testMasterValidDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'MASTER_USER': 'master', 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': test_user['domain']}
        self.runChild(initenv)


    def testMasterValidDomainInvalid(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'MASTER_USER': 'master', 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': 'nonexistantdomain.com'}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)


    def testMasterInvalidNoDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'MASTER_USER': 'master', 'AUTH_USERNAME': 'nonexistantuser'}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)

    def testMasterInvalidDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'MASTER_USER': 'master', 'AUTH_USERNAME': 'nonexistantuser','AUTH_DOMAIN': test_user['domain']}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)




        #userdb checks from postfix
    def testLMTPValid(self):
        initenv = {'SERVICE': 'lmtp', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': test_user['domain']}
        self.runChild(initenv)

    def testLMTPValidDomainInvalid(self):
        initenv = {'SERVICE': 'lmtp', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': 'nonexistantdomain.com'}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)

    def testLMTPInvalid(self):
        initenv = {'SERVICE': 'lmtp', 'AUTH_PASSWORD': '', 'AUTHORIZED': '1', 'AUTH_USERNAME': 'nonexistantuser','AUTH_DOMAIN': test_user['domain']}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)




    def testUserValidNoDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': test_user['password'], 'AUTH_USERNAME': test_user['username']}
        self.runChild(initenv)

    def testUserValidDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': test_user['password'], 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': test_user['domain']}
        self.runChild(initenv)


    def testUserValidDomainInvalid(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': test_user['password'], 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': 'nonexistantdomain.com'}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)


    def testUserValidNoDomainBadPassword(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': 'wrong', 'AUTH_USERNAME': test_user['username']}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,1)

    def testUserValidDomainBadPassword(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': 'wrong', 'AUTH_USERNAME': test_user['username'],'AUTH_DOMAIN': test_user['domain']}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,1)


    def testUserInvalidNoDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': test_user['password'], 'AUTH_USERNAME': 'nonexistantuser'}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)

    def testUserInvalidDomain(self):
        initenv = {'SERVICE': 'imap', 'AUTH_PASSWORD': test_user['password'], 'AUTH_USERNAME': 'nonexistantuser','AUTH_DOMAIN': test_user['domain']}
        ret = self.runChild(initenv,fail=True)
        self.assertEqual(ret,3)

if __name__ == "__main__":
    unittest.main()
