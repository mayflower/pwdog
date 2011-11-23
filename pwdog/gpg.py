import pyme.core
import pyme.constants


class GPGSubkey(object):
    def __init__(self, subkey_t):
        self.subkey_t = subkey_t
        self.fpr = subkey_t.fpr

    def __str__(self):
        #return 'Sub(%s)' % self.subkey_t.keyid
        return self.subkey_t.keyid[8:]


class GPGKey(object):
    def __init__(self, key_t):
        self.key_t = key_t
        self.uids = ['%s <%s>' % (uid.name, uid.email) for uid in key_t.uids]
        self.subkeys = [GPGSubkey(subkey) for subkey in key_t.subkeys]

    def __cmp__(self, o):
        if all(a.fpr == b.fpr for a, b in zip(self.subkeys, o.subkeys)):
            return 0
        return 1

    def __str__(self):
        return '[%s] %s' % ('|'.join(map(str, self.subkeys)), ', '.join(map(str, self.uids)))


class GPG(object):
    def __init__(self):
        self.c = pyme.core.Context()
        self.c.set_armor(1)

    def get_cipher_recipients(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        plaintext = pyme.core.Data()

        try:
            self.c.op_decrypt(cipher_data, plaintext)
        except pyme.errors.GPGMEError:
            pass
            
        recipients = [i.keyid for i in self.c.op_decrypt_result().recipients]

        for recipient in recipients:
            self.c.op_keylist_start(recipient, 0)

            while 1:
                key = self.c.op_keylist_next()
                if key is None:
                    break
                yield GPGKey(key)

            
    def get_cipher_signee_keyids(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        message = pyme.core.Data()

        self.c.op_verify(cipher_data, None, message)
        message.seek(0,0)
        yield message.read()

        res = self.c.op_verify_result()
        for sig in res.signatures:
            if sig.summary & pyme.constants.SIGSUM_VALID|pyme.constants.SIGSUM_GREEN:
                yield sig.fpr

    def get_cipher_signees(self, cipher):
        signeekeyids = list(self.get_cipher_signee_keyids(cipher))
        yield signeekeyids[0]

        for key in self.get_keys(signeekeyids[1:]):
            yield key

    def get_keys(self, aliases):
        for alias in aliases:
            self.c.op_keylist_start(alias, 0)

            while 1:
                key = self.c.op_keylist_next()
                
                if key is None:
                    break
                    
                yield GPGKey(key)

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
        cipher_recipients = [key.key_t for key in self.get_keys(recipients)]
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
            if signee_key.key_t.can_sign == 1:
                self.c.signers_add(signee_key.key_t)
        
        self.c.op_sign(plaintext, cipher_data, pyme.constants.SIG_MODE_NORMAL)
        result = self.c.op_sign_result()
        
        cipher_data.seek(0,0)
        return cipher_data.read()
