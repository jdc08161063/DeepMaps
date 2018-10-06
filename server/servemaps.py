#!/usr/bin/env python

import getoneimage
from options.test_options import TestOptions
import requests
import gzip
from PIL import Image
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('content-type', 'image/png')
        self.end_headers()

    def gzipencode(self, content):
        out = BytesIO()
        f = gzip.GzipFile(fileobj=out, mode='w', compresslevel=5)
        f.write(content)
        f.close()
        return out.getvalue()

    def do_GET(self):
        o = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(o.query)
        originalUrl = params["originalUrl"][0]
        print("Downloadling " + originalUrl)
        res = requests.get(originalUrl)
        img = Image.open(BytesIO(res.content))
        # img.save("./downloaded.png")

        img_fake = getoneimage.getFakeImage(img)

        # Create a stream in RAM to write the generated image as a PNG.
        byte_io = BytesIO()
        img_fake.save(byte_io, format='PNG')

        # Encode it for a faster transfer (this also works without encoding).
        content = self.gzipencode(byte_io.getvalue())

        # Send the image to the client.
        self.send_response(200)
        self.send_header('content-type', 'image/png')
        self.send_header("Content-length", str(len(str(content))))
        self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        self.wfile.write(content)
        self.wfile.flush()

    def do_HEAD(self):
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd server...")
    httpd.serve_forever()


if __name__ == '__main__':
    opt = TestOptions().parse()
    getoneimage.setup(opt)
    run()
