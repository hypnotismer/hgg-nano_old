from __future__ import print_function
import os
import json
import requests
import subprocess
import multiprocessing

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sample:

    def __init__(self, directory):  # directory: to the sample DB

        self.directory = directory
        self.mcm_prepid = os.path.basename(self.directory)
        self.mcm_dataset = os.path.basename(os.path.dirname(self.directory))

        # Load prefetch information.
        prefetch = { }
        for file in os.listdir(self.directory):
            if file[:9] == 'prefetch-':
                dest = open(os.path.join(self.directory, file)).read().strip()
                prefetch[file[9:]] = dest
        self.prefetch = prefetch

        # Load ignore information.
        try: ignore = set(open(os.path.join(self.directory, 'ignore')).read().strip().split())
        except Exception: ignore = set()
        self.ignore = ignore

        # Load DAS dataset name(s).
        datasets = [line.strip() for line in open(os.path.join(directory, 'dataset')).read().splitlines() if line.strip()]
        if not datasets:
            raise RuntimeError('empty dataset file in %s' % directory)
        self.datasets = datasets
        self.dataset = datasets[0] if len(datasets) == 1 else '\n'.join(datasets)

        # Load DAS file list.
        try:
            filelist = json.load(open(os.path.join(directory, 'filelist')))
        except Exception:
            if len(datasets) == 1:
                dataset = datasets[0]
                print('querying dataset %s' % dataset)
                filelist = self.query(dataset)
                if not filelist: raise RuntimeError('failed querying dataset %s' % dataset)
            else:
                filelist = []
                for dataset in datasets:
                    print('querying dataset %s' % dataset)
                    dataset_filelist = self.query(dataset)
                    if not dataset_filelist: raise RuntimeError('failed querying dataset %s' % dataset)
                    filelist.extend(json.loads(dataset_filelist))
                filelist = json.dumps(filelist)
            open(os.path.join(directory, 'filelist'), 'w').write(filelist)
            filelist = json.loads(filelist)
        filelist = [file for file in filelist if file['file'][0]['name'] not in self.ignore]
        for file in filelist:
            file = file['file'][0]
            basename = os.path.basename(file['name'])
            if basename not in self.prefetch: continue
            prefetch = self.prefetch[basename]
            if file['name'] != prefetch[-len(file['name']):]:
                raise RuntimeError('mismatched prefetching: %s <-> %s' % (file['name'], prefetch))
            file['name'] = prefetch
        self.filelist = filelist

        # Load optional event number upper limit.
        try:
            self.maxevent = self.adjust_maxevent(int(open(os.path.join(directory, 'maxevent')).read()))
        except Exception:
            self.maxevent = None

        # Load XSDB information.
        try:
            xsdb = json.load(open(os.path.join(directory, 'xsdb')))
        except Exception:
            print('querying xsdb %s' % dataset)
            xsdb = requests.post('https://xsecdb-xsdb-official.app.cern.ch/api/search', json={
                'orderBy': [],
                'pagination': { 'currentPage': 0, 'pageSize': 0 },
                'search': { 'DAS': self.mcm_dataset },
            }).text
            open(os.path.join(directory, 'xsdb'), 'w').write(xsdb)
            xsdb = json.loads(xsdb)
        self.xsdb = xsdb

        # Load cross section.
        try:
            xs = json.load(open(os.path.join(directory, 'xs')))
        except Exception:
            xs = self.generate_xs()
            open(os.path.join(directory, 'xs'), 'w').write(json.dumps(xs))
        self.xs = xs

    def __repr__(self):

        return '<%d files in %s>' % (len(self.filelist), self.dataset)

    def _file_uri(self, path):
        if path[:5] == 'file:':
            return path[5:]
        return path

    def _parse_root_url(self, url):
        url = self._file_uri(url)
        if url[:7] != 'root://':
            raise RuntimeError('not a root:// url: %s' % url)
        rest = url[7:]
        slash = rest.find('/')
        if slash < 0:
            return url, ''
        return 'root://' + rest[:slash], rest[slash:]

    def _join_root_url(self, server, path):
        if path[:7] == 'root://':
            return path
        if not path.startswith('/'):
            path = '/' + path
        return server + path

    def query(self, dataset):

        if dataset[:5] == 'file:':
            target = dataset[5:]
            if target[:7] == 'root://':
                return self._query_xrootd(target)
            return self._query_local(target)
        if dataset[:7] == 'root://':
            return self._query_xrootd(dataset)
        return os.popen("dasgoclient -json -query='file dataset=%s'" % dataset).read()

    def _query_local(self, directory):
        filelist = []
        for file in os.listdir(directory):
            if file[-5:] != '.root': continue
            file = os.path.join(directory, file)
            if os.stat(file).st_size < 1024 * 1024: continue
            filelist.append({'file': [{'name': 'file:' + file}]})
        filelist = self._count_nevents_all(filelist)
        return json.dumps(filelist)

    def _query_xrootd(self, directory):
        server, path = self._parse_root_url(directory)
        listing = subprocess.check_output(['xrdfs', server, 'ls', path]).decode().splitlines()
        filelist = []
        for line in listing:
            line = line.strip()
            if not line.endswith('.root'): continue
            filelist.append({'file': [{'name': 'file:' + self._join_root_url(server, line)}]})
        if not filelist:
            raise RuntimeError('no .root files found in %s' % directory)
        filelist = self._count_nevents_all(filelist)
        return json.dumps(filelist)

    def _count_nevents_all(self, filelist):
        results = multiprocessing.Pool().map(self.count_nevents, filelist)
        results = [file for file in results if file is not None]
        if not results:
            raise RuntimeError('no readable .root files found')
        return results

    def count_nevents(self, file):
        name = file['file'][0]['name']
        try:
            import ROOT
            tfile = ROOT.TFile.Open(self._file_uri(name))
            if not tfile or tfile.IsZombie():
                raise RuntimeError('failed opening %s' % name)
            nevents = tfile.Get('Events').GetEntriesFast()
            tfile.Close()
            file['file'][0]['nevents'] = nevents
            print(file)
            return file
        except Exception as exc:
            print('skipping %s: %s' % (name, exc))
            return None

    def select(self, target_nevents=None, prefix='root://cms-xrd-global.cern.ch/'):

        if target_nevents is None: target_nevents = self.maxevent
        filelist = []
        nevents = 0
        for file in self.filelist:
            if target_nevents is not None and nevents >= target_nevents: break
            file = file['file'][0]
            name = file['name']
            if name[:5] != 'file:': name = prefix + name
            else: name = name[5:]
            nevents += file['nevents']
            filelist.append((file['nevents'], name))
        return filelist

    def count(self):
        return sum(file['file'][0]['nevents'] for file in self.filelist)

    def adjust_maxevent(self, maxevent):
        filelist = self.select(maxevent)
        return sum(file[0] for file in filelist)

    def generate_xs(self):
        xsdb = self.xsdb
        if len(xsdb) == 0: return
        if len(xsdb) == 1: return xsdb[0]
        for i, item in enumerate(xsdb):
            print('[%d]' % i, item['status'], item['MCM'], item['energy'],
                  item['cross_section'], item['total_uncertainty'], sep='\t')
        while True:
            try:
                return xsdb[int(input('Choice for %s: ' % self.mcm_prepid))]
            except Exception:
                pass

def list_samples(directory=None):  # directory: to the 'samples' DB

    directory = directory or os.path.join(basedir, 'samples')
    samples = { }

    # Directory level 1/2: MCM dataset names
    datasets = os.listdir(directory)
    for dataset in datasets:
        dataset_dir = os.path.join(directory, dataset)
        if not os.path.isdir(dataset_dir): continue

        dataset_samples = { }
        samples[dataset] = dataset_samples

        # Directory level 2/2: MCM prepids
        prepids = os.listdir(dataset_dir)
        for prepid in prepids:
            prepid_dir = os.path.join(dataset_dir, prepid)
            if not os.path.isdir(prepid_dir): continue

            dataset_samples[prepid] = Sample(prepid_dir)  # placeholder

    return samples
