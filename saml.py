import urllib
import base64
from urlparse import parse_qsl, urlsplit
from zlib import decompress, compress
from xml.dom.minidom import parseString
from lxml import etree
from saml2.server import Server
from defusedxml.ElementTree import fromstring
from saml2.sigver import extract_rsa_key_from_x509_cert, RSACrypto, verify_redirect_signature

def base64_decode(encoded_XML):
    print '\nDecoding base64...\n'
    return base64.b64decode(encoded_XML)

def base64_encode(xml):
    print '\nEncoding base64...\n'
    return base64.b64encode(xml)

def url_decode(url):
    print '\nDecoding url percent-encoding...\n'
    while '%' in url:
        url = urllib.unquote(url)

    return url

def url_encode(url):
    return urllib.quote(url)

def get_string_from_file(filename):
    with open(filename, 'r') as my_file:
        data = my_file.read()
    return data


def inflate(data):
    print '\nInflating compressed data...\n'
    return decompress(data, -15)

def deflate(data):
    print '\nCompressing data...\n'
    return compress(data)[2:-4]

def pretty_xml(xml_string):
    print parseString(xml_string).toprettyxml(indent='    ', newl='\n')


def decode_request(saml_request):
    return inflate(base64_decode(url_decode(saml_request)))

def encode_request(saml_request):
    return url_encode(base64_encode(deflate(saml_request)))

def create_IdP():
    return Server('idp_conf')

def unpretty_xml(xml_str):
    parser = etree.XMLParser(remove_blank_text=True)
    elem = etree.XML(xml_str, parser=parser)
    return etree.tostring(elem)

def append_to_file(filename, text):
    with open(filename, 'a') as my_file:
        my_file.write('\n')
        my_file.write(text)

def is_safe_xml(text):
    try:
        fromstring(text, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except Exception as e:
        print(e)
        return False
    return True

def verify_signature(url, cert='/home/ashima/Rackspace/astra-service-providers/dev_ssl/sso_cert'):
    try:
        cert = open(cert, 'r').read().splitlines(True) # cert is path to certfile
        cert = ''.join(cert[1:-1]) # Remove begin cert and end cert lines
    except IOError:
        pass # cert is the certificate
    else:
        print(cert)

    crypto = RSACrypto('dummy key') # The key is not required in this case

    saml_msg = dict(parse_qsl(urlsplit(url).query))

    return verify_redirect_signature(saml_msg, crypto, cert=cert)
