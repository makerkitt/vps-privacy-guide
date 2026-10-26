"""Check template safety and, optionally, parse with the pinned real core."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExamplesTest(unittest.TestCase):
    def config(self, name):
        path = ROOT / 'examples' / f'{name}.json'
        self.assertTrue(path.is_file(), f'Missing {path.name}')
        return json.loads(path.read_text())

    def test_three_matching_protocols_and_credentials(self):
        server = {x['type']: x for x in self.config('server')['inbounds']}
        client = {x['type']: x for x in self.config('client')['outbounds']
                  if x['type'] != 'selector'}
        self.assertEqual(set(server), {'anytls', 'hysteria2', 'vless'})
        self.assertEqual(set(client), set(server))
        for protocol in server:
            with self.subTest(protocol=protocol):
                self.assertEqual(server[protocol]['listen_port'], client[protocol]['server_port'])
                key = 'uuid' if protocol == 'vless' else 'password'
                self.assertEqual(server[protocol]['users'][0][key], client[protocol][key])
        self.assertEqual(server['vless']['users'][0]['flow'], client['vless']['flow'])
        self.assertEqual(server['vless']['tls']['reality']['short_id'][0],
                         client['vless']['tls']['reality']['short_id'])

    def test_tls_verification_is_enabled(self):
        for node in self.config('client')['outbounds']:
            if node['type'] == 'selector':
                continue
            self.assertTrue(node['tls']['enabled'])
            self.assertIs(node['tls'].get('insecure', False), False)
            if node['type'] in {'anytls', 'hysteria2'}:
                self.assertEqual(node['tls']['server_name'], '__TLS_SERVER_NAME__')

    def test_client_proxy_is_loopback_only(self):
        for inbound in self.config('client')['inbounds']:
            self.assertEqual(inbound['listen'], '127.0.0.1')

    def test_compose_has_separate_transports_and_private_admin(self):
        path = ROOT / 'deploy' / 'compose.yaml'
        self.assertTrue(path.is_file())
        compose = path.read_text()
        for binding in ['127.0.0.1:2095:2095/tcp', '127.0.0.1:2096:2096/tcp',
                        '443:443/tcp', '443:443/udp', '8443:8443/tcp']:
            self.assertIn('"' + binding + '"', compose)
        self.assertIn('@sha256:', compose)
        self.assertNotIn('privileged: true', compose)
        self.assertNotIn('network_mode: host', compose)

    def test_credentials_are_explicit_placeholders(self):
        for inbound in self.config('server')['inbounds']:
            for user in inbound['users']:
                credential = user.get('uuid', user.get('password'))
                self.assertRegex(credential, r'^__[A-Z_]+__$')
        key = self.config('server')['inbounds'][2]['tls']['reality']['private_key']
        self.assertEqual(key, '__REALITY_PRIVATE_KEY__')

    @unittest.skipUnless(os.environ.get('VALIDATE_CORE') == '1', 'set VALIDATE_CORE=1 for Docker core checks')
    def test_real_core_accepts_rendered_server_and_client(self):
        versions = json.loads((ROOT / 'versions.json').read_text())
        image = versions['sing_box_image']

        def run(args):
            result = subprocess.run(args, text=True, capture_output=True)
            if result.returncode:
                # Do not echo rendered configs or generated private keys.
                self.fail(f'Command failed: {args[0]} (exit {result.returncode})\n{result.stderr}')
            return result.stdout

        with tempfile.TemporaryDirectory(prefix='sui-vps-check-') as directory:
            tmp = Path(directory)
            run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                 '-keyout', str(tmp / 'key.pem'), '-out', str(tmp / 'cert.pem'),
                 '-days', '1', '-subj', '/CN=example.com'])
            keys = run(['docker', 'run', '--rm', '--network', 'none', image,
                        'generate', 'reality-keypair'])
            private = re.search(r'PrivateKey:\s*(\S+)', keys).group(1)
            public = re.search(r'PublicKey:\s*(\S+)', keys).group(1)
            values = {
                '__SERVER_IP__': '192.0.2.1', '__TLS_SERVER_NAME__': 'example.com',
                '__ANYTLS_PASSWORD__': 'test-only-anytls-password',
                '__HYSTERIA_PASSWORD__': 'test-only-hysteria-password',
                '__VLESS_UUID__': '9f740afa-195d-4cb8-b528-9dcd8529f881',
                '__REALITY_PRIVATE_KEY__': private, '__REALITY_PUBLIC_KEY__': public,
                '__REALITY_SHORT_ID__': '0123456789abcdef',
                '__REALITY_SERVER_NAME__': 'example.com',
                '__REALITY_HANDSHAKE_SERVER__': 'example.com',
                '__CERTIFICATE_PATH__': '/work/cert.pem', '__KEY_PATH__': '/work/key.pem',
            }
            for name in ['server', 'client']:
                self.config(name)
                content = (ROOT / 'examples' / f'{name}.json').read_text()
                for old, new in values.items():
                    content = content.replace(old, new)
                self.assertNotRegex(content, r'__[A-Z_]+__')
                (tmp / f'{name}.json').write_text(content)
                run(['docker', 'run', '--rm', '--network', 'none',
                     '-v', f'{directory}:/work:ro', image,
                     'check', '-c', f'/work/{name}.json'])


if __name__ == '__main__':
    unittest.main()
