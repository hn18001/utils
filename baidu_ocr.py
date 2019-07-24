#!/usr/bin/python
#encoding=utf8

import os
import sys
import urllib
import urllib2
import json
import hashlib
import hmac
import time
import datetime
import base64
from urllib import urlencode
import urllib2
from urllib import quote
from urlparse import urlparse

def gen_auth(access_key, secret_key, utc_time_str, url, method):
    url_parse_ret = urlparse(url)
    host = url_parse_ret.hostname
    path = url_parse_ret.path
    version = "1"
    expiration_seconds = 5   #"1800"
    signature_headers = "host"

    # 1 Generate SigningKey
    val = "bce-auth-v%s/%s/%s/%s" % (version, access_key, utc_time_str, expiration_seconds)
    signing_key = hmac.new(secret_key, val, hashlib.sha256).hexdigest().encode('utf-8')

    # 2 Generate CanonicalRequest
    # 2.1 Genrate CanonicalURI
    canonical_uri = quote(path)
    # 2.2 Generate CanonicalURI: not used here
    # 2.3 Generate CanonicalHeaders: only include host here
    canonical_headers = "host:%s" % quote(host).strip()
    # 2.4 Generate CanonicalRequest
    canonical_request = "%s\n%s\n\n%s" % (method.upper(), canonical_uri, canonical_headers)

    # 3 Generate Final Signature
    signature = hmac.new(signing_key, canonical_request, hashlib.sha256).hexdigest()
    authorization = "bce-auth-v%s/%s/%s/%s/%s/%s" % (version, access_key, utc_time_str, expiration_seconds, signature_headers, signature)
    print authorization
    return authorization

def get_image(filename):
    file = open(filename)
    image = file.read()
    imageStr =  base64.b64encode(image)
    return imageStr

def get_ocr(filename):
    print filename
    access_key = “”
    secret_key = “”
    url = "http://word.bj.baidubce.com/api/v1/ocr/general"
    method = "POST"
    utc_time = datetime.datetime.utcnow()
    utc_time_str = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    auth = gen_auth(access_key, secret_key, utc_time_str, url, method)
    header = {
        'Host':'word.bj.baidubce.com',
        'x-bce-date': utc_time_str,
        'authorization': auth,
        'accept':'*/*'
    }

    data = {
        'appid': '31cdafe9d03e4afd93de2c49c785c9cb',
        'image': get_image(filename)
    }

    request = urllib2.Request(url, urllib.urlencode(data), header)
    response = None
    try :
        response = urllib2.urlopen(request, timeout = 3)
        post_res_str = response.read()
        data = json.loads(post_res_str)

        return data
    except Exception as e:
        #print e.read()
        print e
        return None

def process(dir):
    result_file = open("./result.txt", "w")
    list_dirs = os.walk(dir)
    for root, dirs, files in list_dirs:
        for img_file in files:
            timeout_account = 0
            data = get_ocr(root + img_file)
            print data

            while (timeout_account < 10):       # Time out, reconnect
                if data == None:
                    timeout_account += 1
                    print "timeout:", timeout_account
                    time.sleep(3)
                    data = get_ocr(root+img_file)
                    print data
                else:
                    break;

            if timeout_account == 10:       # timeout!
                result_line = img_file + "\t" + "timeout!\n"
                result_file.write(result_line)
                continue

            ocr_result = ""
            if "error_code" in data:
                ocr_result = data["error_msg"].encode("utf-8")
            else:
                if int(data["words_result_num"]) != 0:
                    ocr_result = data["words_result"][0]["words"].encode("utf-8")

            result_line = img_file + "\t" + ocr_result + "\n"
            result_file.write(result_line)
            time.sleep(1)
    result_file.close()

if __name__ == "__main__":
    dir_name = "./Error_Img/"
    #dir_name = "./test/"
    process(dir_name)

