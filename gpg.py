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

    def decrypt(self, cipher):
        cipher_data = pyme.core.Data(cipher)
        message = pyme.core.Data()

        self.c.op_decrypt(cipher_data, message)

        message.seek(0,0)
        return message.read()

