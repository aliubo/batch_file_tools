import os
import sys
from misc import *


def init_batch_dir(dir_path: str):
    # 创建目录
    if _check_batch_dir(dir_path):
        raise FileExistsError("The directory is already a batch directory")
    if os.path.exists(dir_path) and _has_any_subdir(dir_path):
        raise FileExistsError('The directory has subdirectories')
    p = os.path.join(dir_path, BATCH_DIR_SYMBOL_NAME)
    os.makedirs(p, mode=DIR_MODE)
        

def _has_any_subdir(dir_path: str):
    for root, dirs, files in os.walk(dir_path):
        if dirs:
            return True
    return False


def _check_batch_dir(dir_path: str) -> bool:
    """
    Check if the directory is a batch directory
    :param dir_path: the path of the directory
    :return: True if the directory is a batch directory, False otherwise
    """
    if os.path.isfile(dir_path):
        raise NotADirectoryError("The path is a file, not a directory")
    batch_cfg_dir = os.path.join(dir_path, BATCH_DIR_SYMBOL_NAME)
    if os.path.isfile(batch_cfg_dir):
        raise NotADirectoryError(f'The {batch_cfg_dir} is a file, not a directory')
    return os.path.exists(batch_cfg_dir)


def _get_batch_root_dir(curr_path: str) -> (str, list[str]):
    curr_nodes = []
    for _ in range(curr_path.count(os.sep) + 1):
        if _check_batch_dir(curr_path):
            curr_nodes = curr_nodes[::-1]
            return curr_path, curr_nodes
        curr_nodes.append(os.path.basename(curr_path))
        curr_path = os.path.dirname(curr_path)
    raise BatchDirNotFoundError('Cannot find the batch directory')


def organize_files(curr_path: str):
    curr_path = os.path.abspath(curr_path)
    root_dir, curr_nodes = _get_batch_root_dir(curr_path)
    _organize_files(root_dir, curr_nodes)


def _join_paths(root_dir, curr_nodes: list[str], filename=None):
    res = os.path.join(root_dir, os.sep.join(curr_nodes))
    if filename:
        res = os.path.join(res, filename)
    return res


def _organize_files(root_dir: str, curr_nodes: list[str]):
    """
    """
    curr_dir = _join_paths(root_dir, curr_nodes)
    filenames = []
    for f in os.scandir(curr_dir):
        if f.is_dir():
            continue
        if _try_move_if_exists(root_dir, curr_nodes, f.name):
            continue
        if _split_filename(f.name) == curr_nodes:
            continue
        filenames.append(f.name)
    if len(filenames) > MAX_FILE:
        _try_move(root_dir, curr_nodes, filenames)


def _try_move(root_dir: str, curr_nodes: list[str], filenames: list[str]):
    curr_dir = _join_paths(root_dir, curr_nodes)
    # 将最多的公共前缀创建文件夹
    discard_prefix = len(curr_nodes)
    prefixes = set()
    prefix2filenames = {}
    for name in filenames:
        sf = _split_filename(name)
        prefix = sf[discard_prefix] if len(sf) > discard_prefix else ''
        prefixes.add(prefix)
        prefix2filenames.setdefault(prefix, []).append(name)
    prefix_num_sorted = sorted({p: len(ns) for p, ns in prefix2filenames.items()}.items(), key=lambda x: x[1])
    rest_file_num = len(filenames)
    while rest_file_num > MAX_FILE:
        prefix, num = prefix_num_sorted.pop()
        rest_file_num -= num
        prefixes.remove(prefix)
        dst_dir = os.path.join(curr_dir, prefix)
        os.mkdir(dst_dir, mode=DIR_MODE)
        prefixfiles = prefix2filenames.pop(prefix)
        for filename in prefixfiles:
            os.rename(
                src=os.path.join(curr_dir, filename),
                dst=os.path.join(dst_dir, filename)
            )
        _try_move(root_dir, curr_nodes + [prefix], prefixfiles)


def _try_move_if_exists(root_dir: str, curr_nodes: list[str], filename: str) -> bool:
    file_nodes = _split_filename(filename)
    if curr_nodes == file_nodes:
        return True
    while True:
        if not file_nodes:
            break
        target_dir = _join_paths(root_dir, file_nodes)
        if os.path.exists(target_dir):
            os.rename(
                src=_join_paths(root_dir, curr_nodes, filename),
                dst=_join_paths(root_dir, file_nodes, filename),
            )
            return True
        file_nodes.pop()
    if curr_nodes == file_nodes[:len(curr_nodes)]:
        return False
    else:
        os.rename(
            src=_join_paths(root_dir, curr_nodes, filename),
            dst=os.path.join(root_dir, filename)
        )
        return True


def _split_filename(filename: str) -> list[str]:
    if IGOURE_SUFFIX and '.' in filename:
        filename = filename[:filename.rfind('.')]
    filename = filename.replace(' ', '_')
    res = []
    reslen = len(filename) // SPLIT_LEN
    for i in range(reslen):
        res.append(filename[i * SPLIT_LEN:(i + 1) * SPLIT_LEN])
    return res


class open(object):
    def __init__(self, root_dir, filename, mode, *args, **kwargs):
        import builtins
        sf = _split_filename(filename)
        real_dir = root_dir
        for node in sf:
            next_path = os.path.join(real_dir, node)
            if os.path.exists(next_path):
                real_dir = next_path
            else:
                break
        real_path = os.path.join(real_dir, filename)
        self._f = builtins.open(real_path, mode, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._f.close()
    
