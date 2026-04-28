import errno
import io
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request as urllib

from functools import partial
from urllib.request import urlopen

from gensim.downloader import BASE_DIR, logger, _PARENT_DIR, DATA_LIST_URL, DOWNLOAD_BASE_URL, _get_parts, _progress, \
    _get_checksum, _calculate_md5_checksum
from gensim.models import KeyedVectors


class Model:
    shared_model = None
    def load_model(self, name):
        if Model.shared_model is not None:
            return Model.shared_model
        self.create_base_dir()
        file_name = self.get_filename(name)
        if file_name is None:
            raise ValueError("Incorrect model/corpus name")
        folder_dir = os.path.join(BASE_DIR, name)

        fast_model_path = os.path.join(folder_dir, f"{name}_fast.gensim")
        if os.path.exists(fast_model_path):
            logger.info("Znaleziono zoptymalizowany plik .gensim. Błyskawiczne ładowanie (mmap)...")
            start_time = time.time()
            Model.shared_model = KeyedVectors.load(fast_model_path, mmap='r')
            load_time = time.time() - start_time
            print(f"Czas ładowania modelu {name} zoptymalizowany do {load_time:.2f}s")
            return Model.shared_model

        if not os.path.exists(folder_dir):
            self.download(name)

        sys.path.insert(0, BASE_DIR)
        module = __import__(name)
        loaded_model = module.load_data()
        loaded_model.save(fast_model_path)
        Model.shared_model = loaded_model
        return Model.shared_model
    def create_base_dir(self):
        if not os.path.isdir(BASE_DIR):
            try:
                logger.info("Creating %s", BASE_DIR)
                os.makedirs(BASE_DIR)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    raise Exception(
                        "Not able to create folder gensim-data in {}. File gensim-data "
                        "exists in the directory already.".format(_PARENT_DIR)
                    )
                else:
                    raise Exception(
                        "Can't create {}. Make sure you have the read/write permissions "
                        "to the directory or you can try creating the folder manually"
                        .format(BASE_DIR)
                    )
    def get_filename(self, name):
        information = self.info()
        corpora = information['corpora']
        models = information['models']
        if name in corpora:
            return information['corpora'][name]["file_name"]
        elif name in models:
            return information['models'][name]["file_name"]
    def info(self):
        information = self.load_info()

        return {
            "corpora": {name: data for (name, data) in information['corpora'].items() if data.get("latest", True)},
            "models": {name: data for (name, data) in information['models'].items() if data.get("latest", True)}
        }
    def load_info(self,url=DATA_LIST_URL, encoding='utf-8'):

            """Load dataset information from the network.

            If the network access fails, fall back to a local cache.  This cache gets
            updated each time a network request _succeeds_.
            """
            cache_path = os.path.join(BASE_DIR, 'information.json')
            self.create_base_dir()

            try:
                info_bytes = urlopen(url).read()
            except (OSError, IOError):
                logger.exception(
                    'caught non-fatal exception while trying to update gensim-data cache from %r; '
                    'using local cache at %r instead', url, cache_path
                )
            else:
                with open(cache_path, 'wb') as fout:
                    fout.write(info_bytes)

            try:
                #
                # We need io.open here because Py2 open doesn't support encoding keyword
                #
                with io.open(cache_path, 'r', encoding=encoding) as fin:
                    return json.load(fin)
            except IOError:
                raise ValueError(
                    'unable to read local cache %r during fallback, '
                    'connect to the Internet and retry' % cache_path
                )
    def download(self, name):
        url_load_file = "{base}/{fname}/__init__.py".format(base=DOWNLOAD_BASE_URL, fname=name)
        data_folder_dir = os.path.join(BASE_DIR, name)
        data_folder_dir_tmp = data_folder_dir + '_tmp'
        tmp_dir = tempfile.mkdtemp()
        init_path = os.path.join(tmp_dir, "__init__.py")
        urllib.urlretrieve(url_load_file, init_path)
        total_parts = _get_parts(name)
        if total_parts > 1:
            concatenated_folder_name = "{fname}.gz".format(fname=name)
            concatenated_folder_dir = os.path.join(tmp_dir, concatenated_folder_name)
            for part in range(0, total_parts):
                url_data = "{base}/{fname}/{fname}.gz_0{part}".format(base=DOWNLOAD_BASE_URL, fname=name, part=part)

                fname = "{f}.gz_0{p}".format(f=name, p=part)
                dst_path = os.path.join(tmp_dir, fname)
                urllib.urlretrieve(
                    url_data, dst_path,
                    reporthook=partial(_progress, part=part, total_parts=total_parts)
                )
                if _calculate_md5_checksum(dst_path) == _get_checksum(name, part):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    logger.info("Part %s/%s downloaded", part + 1, total_parts)
                else:
                    shutil.rmtree(tmp_dir)
                    raise Exception("Checksum comparison failed, try again")
            with open(concatenated_folder_dir, 'wb') as wfp:
                for part in range(0, total_parts):
                    part_path = os.path.join(tmp_dir, "{fname}.gz_0{part}".format(fname=name, part=part))
                    with open(part_path, "rb") as rfp:
                        shutil.copyfileobj(rfp, wfp)
                    os.remove(part_path)
        else:
            url_data = "{base}/{fname}/{fname}.gz".format(base=DOWNLOAD_BASE_URL, fname=name)
            fname = "{fname}.gz".format(fname=name)
            dst_path = os.path.join(tmp_dir, fname)
            urllib.urlretrieve(url_data, dst_path, reporthook=_progress)
            if _calculate_md5_checksum(dst_path) == _get_checksum(name):
                sys.stdout.write("\n")
                sys.stdout.flush()
                logger.info("%s downloaded", name)
            else:
                shutil.rmtree(tmp_dir)
                raise Exception("Checksum comparison failed, try again")

        if os.path.exists(data_folder_dir_tmp):
            os.remove(data_folder_dir_tmp)

        shutil.move(tmp_dir, data_folder_dir_tmp)
        os.rename(data_folder_dir_tmp, data_folder_dir)
