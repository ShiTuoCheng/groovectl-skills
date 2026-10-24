import http.server, threading, subprocess, os, tempfile, pathlib, re, shlex, json, shutil, argparse
repo = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description='Check documented commands against the published CLI and a loopback fixture, never a real Discogs account.')
parser.add_argument('--cli', default=shutil.which('groovectl'), help='Path to the installed groovectl executable (defaults to PATH)')
options = parser.parse_args()
if not options.cli:
    parser.error('groovectl not found; follow README.md CLI installation steps or pass --cli')
binpath = str(pathlib.Path(options.cli).resolve())
requests = []
base = 'https://api.discogs.com'
basic = {'id':249504,'title':'Fixture Album','resource_url':base+'/releases/249504','year':1959,'artists':[{'name':'Fixture Artist'}], 'formats':[{'name':'Vinyl'}]}
item = {'id':249504,'instance_id':123456,'folder_id':1,'rating':5,'basic_information':basic}
want = {'id':249504,'rating':5,'notes':'Fixture notes','resource_url':base+'/releases/249504','basic_information':basic}
pagination = {'page':1,'pages':1,'items':1,'per_page':50,'urls':{}}
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def respond(self):
        path = self.path.split('?')[0]
        requests.append((self.command,path))
        data = None
        status = 200
        if self.command == 'DELETE' or '/instances/' in path:
            status = 204
        elif path == '/oauth/identity':
            data = {'id':1,'username':'fixture-user','resource_url':base+'/users/fixture-user'}
        elif path == '/releases/249504': data = basic
        elif path == '/database/search':
            data = {'pagination':pagination,'results':[{'id':249504,'type':'release','title':'Fixture Album','country':'Japan','year':'1959','format':['Vinyl'],'label':['Fixture'],'catno':'TEST-1','resource_url':base+'/releases/249504'}]}
        elif path == '/masters/5460':
            data = {'id':5460,'title':'Fixture Album','year':1959,'main_release':249504,'resource_url':base+path,'uri':'https://www.discogs.com/master/5460'}
        elif path == '/masters/5460/versions':
            data = {'pagination':pagination,'versions':[{'id':249504,'title':'Fixture Album','label':'Fixture','country':'Japan','released':'1959','format':'Vinyl','catno':'TEST-1','resource_url':base+'/releases/249504'}]}
        elif path in ['/artists/45','/labels/1']:
            data = {'id':int(path.rsplit('/',1)[1]),'name':'Fixture','resource_url':base+path,'uri':'https://www.discogs.com'+path}
        elif path in ['/artists/45/releases','/labels/1/releases']:
            data = {'pagination':pagination,'releases':[{'id':249504,'title':'Fixture Album','type':'release','artist':'Fixture Artist','role':'Main','resource_url':base+'/releases/249504'}]}
        elif path.endswith('/collection/folders'):
            data = {'folders':[{'id':1,'count':1,'name':'Uncategorized','resource_url':base+path+'/1'},{'id':2,'count':0,'name':'Fixture','resource_url':base+path+'/2'}]}
        elif path.endswith('/collection/value'):
            data = {'minimum':'$1.00','median':'$2.00','maximum':'$3.00'}
        elif '/collection/' in path:
            if self.command == 'POST': data = {'instance_id':123456,'resource_url':base+path}
            else: data = {'pagination':pagination,'releases':[item]}
        elif path.endswith('/wants'): data = {'pagination':pagination,'wants':[want]}
        elif '/wants/' in path: data = want
        elif '/marketplace/stats/' in path:
            data = {'lowest_price':None,'num_for_sale':None,'blocked_from_sale':True}
        elif '/marketplace/listings/' in path:
            data = {'id':123456789,'status':'For Sale','price':{'value':45,'currency':'EUR'},'condition':'Near Mint (NM or M-)','seller':{'username':'fixture-seller'},'release':{'id':249504,'description':'Fixture Album'}}
        elif '/marketplace/fee/' in path: data = {'value':4.05,'currency':'USD'}
        else: status=404; data={'message':'Unexpected fixture route: '+path}
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        if status!=204: self.wfile.write(json.dumps(data).encode())
    do_GET=respond
    do_POST=respond
    do_PUT=respond
    do_DELETE=respond
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with tempfile.TemporaryDirectory(prefix='groovectl-skill-fixture-') as config:
    env={**os.environ,'NODE_ENV':'test','GROOVECTL_CONFIG_DIR':config,'GROOVECTL_API_BASE_URL':f'http://127.0.0.1:{server.server_port}','DISCOGS_TOKEN':'synthetic-fixture-token-not-a-user-secret'}
    doc=(repo/'skills/groovectl/references/commands.md').read_text()
    commands=[line for block in re.findall(r'```sh\n(.*?)```',doc,re.S) for line in block.splitlines() if line.startswith('groovectl ')]
    commands+=['groovectl auth status --json']
    for line in commands:
        args=shlex.split(line)[1:]
        before=len(requests)
        p=subprocess.run([binpath,*args],env=env,text=True,capture_output=True,timeout=20)
        assert p.returncode==0, (line,p.returncode,p.stderr)
        if '--dry-run' in args:
            assert all(method=='GET' for method,path in requests[before:]), line
            assert json.loads(p.stdout)['dryRun'] is True
        if '--json' in args: result=json.loads(p.stdout)
        if args[:2]==['marketplace','stats']:
            assert result['lowestPrice'] is None and result['numForSale'] is None and result['blockedFromSale'] is True
        if args[:2]==['collection','contains']:
            assert isinstance(result,list) and result[0]['instanceId']==123456
        print('PASS',line)
    print(f'VALIDATED {len(commands)} commands against isolated fixture; {len(requests)} local HTTP requests.')
server.shutdown()
