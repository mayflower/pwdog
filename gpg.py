import pyme.core
import pyme.constants

class GPG(object):
    def __init__(self):
        self.c = pyme.core.Context()
        self.c.set_armor(1)

    def get_cipher_fingerprints(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        foo = pyme.core.Data()

        try:
            self.c.op_decrypt(cipher_data, foo)
        except pyme.errors.GPGMEError:
            pass

        recipients = [i.keyid for i in self.c.op_decrypt_result().recipients]

        for recipient in recipients:
            self.c.op_keylist_start(recipient, 0)

            while 1:
                key = self.c.op_keylist_next()
                if key is None:
                    break
                for subkey in key.subkeys:
                    yield subkey.fpr

    def get_cipher_signees(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        message = pyme.core.Data()

        self.c.op_verify(cipher_data, None, message)
        message.seek(0,0)
        yield message.read()

        res = self.c.op_verify_result()
        for sig in res.signatures:
            if sig.summary & pyme.constants.SIGSUM_VALID:
                yield sig.fpr

    def get_keys(self, aliases):
        for alias in aliases:
            self.c.op_keylist_start(alias, 0)

            while 1:
                key = self.c.op_keylist_next()
                
                if key is None:
                    break
                    
                yield key

    def get_subkeys(self, aliases):
        for alias in aliases:
            self.c.op_keylist_start(alias, 0)

            while 1:
                key = self.c.op_keylist_next()
                if key is None:
                    break
                
                for subkey in key.subkeys:
                    yield subkey

    def decrypt(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        message = pyme.core.Data()

        self.c.op_decrypt(cipher_data, message)

        message.seek(0,0)
        return message.read()

    def encrypt(self, recipients, plaintext):
        cipher_data = pyme.core.Data()
        cipher_recipients = list(self.get_keys(recipients))
        message = pyme.core.Data(plaintext)

        self.c.op_encrypt(cipher_recipients, pyme.constants.ENCRYPT_ALWAYS_TRUST,
                            message, cipher_data)

        cipher_data.seek(0,0)
        return cipher_data.read()

    def sign(self, signee, message):
        plaintext = pyme.core.Data(message)
        cipher_data = pyme.core.Data()
        signee_keys = list(self.get_keys(signee))
        
        for signee_key in signee_keys:
            if signee_key.can_sign == 1:
                self.c.signers_add(signee_key)
        
        #self.c.op_sign_start(plaintext, cipher_data, pyme.constants.SIG_MODE_NORMAL)
        
        self.c.op_sign(plaintext, cipher_data, pyme.constants.SIG_MODE_NORMAL)
        result = self.c.op_sign_result()
        
        cipher_data.seek(0,0)
        return cipher_data.read()

