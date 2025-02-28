import base64

from Crypto.Cipher import AES


class MightyCrypto:
    block_size = AES.block_size
    cipher_method = AES

    __pad = lambda self, s: s + (
        self.block_size - len(s) % self.block_size
    ) * chr(self.block_size - len(s) % self.block_size)
    __unpad = lambda self, s: s[: -ord(s[len(s) - 1 :])]

    def cipher(self, key, *args, **kwargs):
        return self.ciper_method.new(
            kwargs.get('key')[:32], AES.MODE_CBC, kwargs.get('iv')
        )

    def encrypt_data(self, *args, **kwargs):
        raw = self.__pad(kwargs.get('data'))
        return base64.b64encode(self.cipher(**kwargs).encrypt(raw))

    def decrypt_data(self, *args, **kwargs):
        raw = base64.b64decode(kwargs.get('data'))
        return self.__unpad(self.cipher(**kwargs).decrypt(raw))
