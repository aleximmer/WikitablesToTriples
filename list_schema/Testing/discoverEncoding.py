import codecs
# from lxml import html
import html

# file.read() mir 'rt' gibt UnicodeEncodeError -> Byteweise einlesen
# – (En dash): \xe2\x80\x93
# ñé: \xc3\xb1\xc3\xa9
# file = open('prot.html', 'rb')
with codecs.open('prot2.html', 'r', encoding='UTF-8') as f:
	byteText = f.read()



# Non-ASCII characters are replaced by a XML reference. E.g.: – (En dash) is shown as &#8211;
# https://docs.python.org/3/howto/unicode.html#converting-to-bytes
# text = byteText.encode('ascii', 'xmlcharrefreplace')

# All examples are throwing UnicodeEncodeError because of the \u2013 (En dash) (as hexadecimal number: 8211)
# print(byteText.encode())
print(html.unescape(byteText))
# print(b'\x80'.decode()) # Generates an UnicodeEncodeError (character maps to undefined)