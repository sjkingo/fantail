"""
File-related utility functions.
"""

import filecmp
import os
import shutil

def mirror_tree(src, dest, exclude=None):
    """
    Mirrors a directory tree from `src` to `dest`, taking care not to override
    any files that have not changed. If `exclude` is a (non-empty) list, don't
    mirror changes to any file or directory that matches an element in it.
    The `src` directory must exist, but the `dest` will be created if it
    does not exist. Any files or directories not in the source directory will
    be deleted from the destination, so use this with care!
    """

    if not os.path.isdir(src):
        raise FileNotFoundError(src)

    if exclude is None:
        exclude = set()
    else:
        exclude = set(exclude)

    for root, dirs, files in os.walk(src):
        # Remove any excluded directories so we don't traverse them
        items_to_exclude = exclude & set(dirs)
        for i in items_to_exclude:
            dirs.remove(i)

        # Compute relative paths for the destination
        relative_root = root.replace(src, '')
        if len(relative_root) > 0 and relative_root[0] == os.path.sep:
            relative_root = relative_root[1:]
        dest_dir = os.path.join(dest, relative_root)

        # Create root directory
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)

        # Copy files from src -> dest if they don't exist or hash doesn't match
        for f in files:
            if f in exclude:
                continue
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_dir, f)
            if os.path.isfile(dest_file):
                if filecmp.cmp(src_file, dest_file, shallow=False):
                    # same file
                    continue
            shutil.copyfile(src_file, dest_file)

        # Delete files and directories in destination but not in source
        entries = os.listdir(dest_dir)
        files_in_dest = [f for f in entries if os.path.isfile(os.path.join(dest_dir, f))]
        for f in files_in_dest:
            if f not in files and f not in exclude:
                os.remove(os.path.join(dest_dir, f))
        dirs_in_dest = [d for d in entries if os.path.isdir(os.path.join(dest_dir, d))]
        for d in dirs_in_dest:
            if d not in dirs and d not in exclude:
                shutil.rmtree(os.path.join(dest_dir, d))

def map_input_output_files(input_dir):
    """
    Creates a dictionary of input_file -> output_file of each page in the
    given directory. The directory structure is maintained with each
    subpage being placed in its own directory and named index.html.

    For example:

    /pages
    * index.txt -> /output/index.html
    * /blog
       * hello-world.txt -> /output/blog/hello-world/index.html
       * how-to-use-fantail.txt -> /output/blog/how-to-use-fantail/index.html

    Files not ending in .txt are considered static and will be written as is.
    """

    output_pages = {}

    for root, dirs, files in os.walk(input_dir):
        prefix = root.replace(input_dir, '')
        for p in files:
            if not p.endswith('.txt'):
                # other file, don't perform transformation
                output_filename = os.path.join(prefix, p)
            else:
                # .txt file, transform it
                if p == 'index.txt':
                    output_filename = '/index.html'
                else:
                    title = os.path.splitext(p)[0]
                    output_filename = prefix + '/' + title + '/index.html'

            input_filename = os.path.join(root, p)
            output_pages[input_filename] = output_filename

    return output_pages
