import os
import hashlib
import pandas as pd
from datetime import datetime
import time


class AnalysisFileTree:
    def __init__(self, root, verbose=False, ignore_hidden=False, hash_name=None):
        self.root_dir = root
        self.verbose = verbose
        self.ignore_hidden = ignore_hidden
        self.hash_name = check_hash_name(hash_name)

    def _calculate_hash(self, file_path):
        buffer_size = 262144000
        # buffer_size = 524288000
        with open(file_path, 'rb') as f:
            checksum = getattr(hashlib, self.hash_name)()
            for chunk in iter(lambda: f.read(buffer_size), b''):
                checksum.update(chunk)
            return checksum.hexdigest()

    def _recursive_stats(self, directory_path, items=[], depth=0, idx=1, parent_idx=0):
        directory_size = 0
        number_files = 0
        current_idx = idx

        for file in os.listdir(directory_path):
            if self.ignore_hidden and file.startwith('.'):
                continue

            file_path = os.path.join(directory_path, file)
            stats = os.stat(file_path)
            directory_size += stats.st_size
            idx += 1

            if os.path.isfile(file_path):
                file_name, extension = os.path.splitext(file)
                extension = extension[1:] if extension else None
                if self.verbose:
                    print('FILE : {0} - {1:.3f}MB'.format(file_name, stats.st_size / (1024 * 1024)), end='')
                start_time = time.time()
                item = [idx,
                        file_path,
                        file_name,
                        extension,
                        stats.st_size,
                        stats.st_atime,
                        stats.st_mtime,
                        stats.st_ctime,
                        False,
                        None,
                        depth,
                        current_idx]
                if self.hash_name:
                    item.append(self._calculate_hash(file_path))
                items.append(item)
                number_files += 1
                if self.verbose:
                    print(" - %s seconds" % (time.time() - start_time))
            else:
                if self.verbose:
                    print('FOLDER : {}'.format(file_path))
                idx, items, _directory_size, _number_files = self._recursive_stats(
                    file_path, items, depth + 1, idx, current_idx)
                directory_size += _directory_size
                number_files += _number_files

        stats = os.stat(directory_path)
        directory_name = os.path.basename(directory_path)
        item = [current_idx,
                directory_path,
                directory_name,
                None,
                directory_size,
                stats.st_atime,
                stats.st_mtime,
                stats.st_ctime,
                True,
                number_files,
                depth,
                parent_idx]
        if self.hash_name:
            item.append(None)
        items.append(item)

        return idx, items, directory_size, number_files

    def stats(self):
        columns = ['id',
                   'path',
                   'name',
                   'extension',
                   'size',
                   'atime',
                   'mtime',
                   'ctime',
                   'folder',
                   'num_files',
                   'depth',
                   'parent']
        idx, items, directory_size, number_files = self._recursive_stats(self.root_dir, items=[])
        if self.hash_name:
            columns.append(self.hash_name)

        df = pd.DataFrame(items, columns=columns)
        for col in ['atime', 'mtime', 'ctime']:
            df[col] = df[col].apply(lambda d: datetime.fromtimestamp(d))

        return df


def check_hash_name(hash_name):
    if hash_name:
        hash_name = hash_name.lower()
        if not hasattr(hashlib, hash_name):
            raise Exception('Hash algorithm not available : {} algorithms available {}' \
                            .format(hash_name, hashlib.algorithms_available))
    return hash_name
