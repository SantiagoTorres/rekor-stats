import json
import os
from base64 import b64decode as b64d
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

from collections import Counter

def parse_rekord(self, payload): 
    self._type = payload['Body']['RekordObj']['signature']['format']
    self.artifact_id = payload['Body']['RekordObj']['data']['hash']['value']
    self.provider = None
    try:
        self.author = b64d(payload['Body']['RekordObj']['signature']['publicKey']['content'])
        if self.author.decode('utf-8').startswith("-----BEGIN CERTIFICATE"):
            cert = x509.load_pem_x509_certificate(self.author)
            try:
                if len(cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value) > 1:
                    self.artifact_id = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.GeneralName)
                email = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.RFC822Name)
            except:
                email = ['unknown']

            if len(email) > 0:
                email = email[0]
            else:
                email = "not-found"
            provider_oid = x509.ObjectIdentifier("1.3.6.1.4.1.57264.1.1")

            try:
                oicd = cert.extensions.get_extension_for_oid(provider_oid).value.value.decode("utf-8")
            except x509.extensions.ExtensionNotFound as e:
                oicd = "not found"
            except Exception as e:
                print(e)
                import pdb; pdb.set_trace()
            self.author =  email
            self.provider = oicd
            #print("found cert for author {}".format(self.author))
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
        


def parse_in_toto(self, payload): 
    try:
        attestation = b64d(payload['Attestation'])
        if len(attestation):
            # actualfax cosign payload
            if attestation.decode("utf-8").startswith("# cosign\n\n"):
                link = {'predicateType': "cosign-readme :)"}

            else:
                link = json.loads(attestation)
                if type(link) == list:
                    link = link[0]
        else:
            link = {'predicateType': "opaque"}
        self._type = "in-toto {}".format(link['predicateType'])
        if 'subject' in link and link['subject']:
            if type(link['subject']) == list:
                self.artifact_id = link['subject'][0]['name'] 
            else:
                self.artifact_id = link['subject']['name']
        else:
            self.artifact_id = payload['Body']['IntotoObj']['content']['hash']['value']
        self.author = payload['Body']['IntotoObj']['publicKey']
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()


def parse_hashed_rekord(self, payload): 
    try:
        self._type = payload['Body']['HashedRekordObj']['signature']['format']
        print("lol")
    except:
        self._type = "hashed_rekord"

    self.provider = None
    try:
        self.author = b64d(payload['Body']['HashedRekordObj']['signature']['publicKey']['content'])
        if self.author.decode('utf-8').startswith("-----BEGIN CERTIFICATE"):
            cert = x509.load_pem_x509_certificate(self.author)
            try:
                if len(cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value) > 1:
                    self.artifact_id = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.GeneralName)
                email = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.RFC822Name)
            except:
                email = ['unknown']
            if len(email) > 0:
                email = email[0]
            else:
                email = "not-found"
                provider_oid = x509.ObjectIdentifier("1.3.6.1.4.1.57264.1.1")

            try:
                oicd = cert.extensions.get_extension_for_oid(provider_oid).value.value.decode("utf-8")
            except:
                oicd = "self"
            self.author =  email
            self.provider = oicd
            #print("found cert for author {}".format(self.author))
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()


    self.artifact_id = payload['Body']['HashedRekordObj']['data']['hash']['value']


def parse_rpm(self, payload): 
    payload = payload['Body']["RPMModel"]
    self._type = "rpm"
    self.artifact_id = "{Name}-{Epoch}:{Version}-{Release}-{Architecture}".format(**payload['package']['headers'])
    # FIXME: this should decode the b64 *and* then parse the gpg payload to fetch a uid
    self.author = payload['publicKey']['content']


def parse_rfc3161(self, payload): 
    payload = payload['Body']["Rfc3161Obj"]
    self._type = "RFC3161"
    self.artifact_id = payload['tsr']['content']
    # FIXME: this should decode the b64 *and* then parse the cms payload to fetch a uid
    #self.author = payload['publicKey']['content']


def parse_helm(self, payload): 
    payload = payload['Body']["HelmObj"]
    self._type = "Helm"
    self.artifact_id = payload['chart']['hash']['value']
    # FIXME: this should decode the b64 *and* then parse the cms payload to fetch a uid
    #self.author = payload['publicKey']['content']


def parse_tuf(self, payload): 
    payload = payload['Body']["TufObj"]
    self._type = "Tuf"
    self.artifact_id = "TUF Trust root"
    # FIXME: this should decode the b64 *and* then parse the cms payload to fetch a uid
    self.author = "Sigstore authors"


def parse_jar(self, payload): 
    payload = payload['Body']["JARModel"]
    self._type = "JAR"
    self.artifact_id = payload['archive']['hash']['value']
    # FIXME: this should decode the b64 *and* then parse the cms payload to fetch a uid
    self.author = payload['signature']['publicKey']['content']


def parse_alpine(self, payload): 
    payload = payload['Body']["AlpineModel"]
    self._type = "Alpine"
    try:
        self.artifact_id = payload['package']['pkginfo']['datahash']
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
    # FIXME: this should decode the b64 *and* then parse the cms payload to fetch a uid
    self.author = payload['publicKey']['content']


type_parser_dispatch = {
    "RekordObj": parse_rekord,
    "IntotoObj": parse_in_toto,
    "HashedRekordObj": parse_hashed_rekord,
    "Rfc3161Obj": parse_rfc3161,
    "HelmObj": parse_helm,
    "RPMModel": parse_rpm,
    "JARModel": parse_jar,
    "TufObj": parse_tuf,
    "AlpineModel": parse_alpine,
}



class RekorEntry:

    _type = None
    artifact_id = None
    timestamp = None
    author = None

    def __init__(self, payload):

        keys = [x for x in payload['Body'].keys()]
        assert (len(keys)) == 1
        if keys[0] in type_parser_dispatch:
            type_parser_dispatch[keys[0]](self, payload)
            self.timestamp = payload['IntegratedTime']
        else:
            import pdb; pdb.set_trace()


def get_entry(filename):
    with open(filename) as fp:
        data = fp.read()
    try:
        result = json.loads(data)
    except Exception as e:
        import pdb; pdb.set_trace()
        raise
    return result


if __name__ == "__main__":
    classes = Counter()
    i = 0
    limit = int(1e7)
    for entry in os.listdir("dataset")[:limit]:
        res = get_entry(os.path.join("dataset", entry))
        r = RekorEntry(res)
        classes[r._type] += 1
        

    with open("type_breakdown.json", 'w') as fp:
        json.dump(classes, fp)
    print(classes)
