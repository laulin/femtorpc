import lz4.frame as lz4
from base64 import urlsafe_b64encode
from time import time

from cryptography.fernet import Fernet
import dill



def get_serializer(key:bytes=None, compressed:bool=False)->dict:
    serializer = Serializer(key, compressed)

    return {"loads" : serializer.loads, "dumps": serializer.dumps}

class Serializer:
    def __init__(self, key:bytes=None, compressed:bool=False, compression_algorithm=lz4, ttl:int=30):
        self._compressed = compressed
        self._compression_algorithm = compression_algorithm
        self._ttl = ttl
        
        if key is not None:
            if not isinstance(key, bytes) or len(key) != 32:
                raise Exception("Key must be a 32 bytes string")
            self._key = urlsafe_b64encode(key) # need for fernet
        else:
            self._key = None
        

    def dumps(self, data)->bytes:
        serialized_data = dill.dumps(data)

        if self._compressed:
            serialized_data = self._compression_algorithm.compress(serialized_data)

        if self._key is not None:
            fernet = Fernet(self._key)
            serialized_data = fernet.encrypt(serialized_data)

        return serialized_data


    def loads(self, serialized_data:bytes)->object:
        if self._key is not None:
            fernet = Fernet(self._key)
            if self._ttl is not None:
                serialized_data = fernet.decrypt_at_time(serialized_data, self._ttl, int(time()))
            else:
                serialized_data = fernet.decrypt(serialized_data)

        if self._compressed:
            serialized_data = self._compression_algorithm.decompress(serialized_data)

        return dill.loads(serialized_data)