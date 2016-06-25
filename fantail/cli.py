"""
Command-line interface to the fantail site generator.
setuptools will create a console script pointing to cli:main
"""

import argparse
import logging

from fantail.staticsite import StaticSite

def cmd_init_site(args):
    """
    Creates a new site with default templates.
    """
    site = StaticSite(args.site_directory)
    site.init_site()

def cmd_clean_site(args):
    """
    Removes the output directory from an existing site.
    """
    site = StaticSite(args.site_directory)
    site.clean_site()

def cmd_build_site(args):
    """
    Builds a site by running the generator over the pages directory.
    """
    site = StaticSite(args.site_directory)
    site.build_site()

def parse_args():
    parser = argparse.ArgumentParser(description='fantail is a static site generator')
    subparsers = parser.add_subparsers(dest='cmd', help='Subcommands (type subcommand -h to view help)')

    def add_site_arg(this_parser):
        this_parser.add_argument('site_directory', default='./fantail-site/',
                                 nargs='?', help='Directory where the site is '
                                 'stored. Defaults to %(default)s')

    # Common arguments
    parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Switch on verbose logging')

    # fantail init
    init_parser = subparsers.add_parser('init', description=cmd_init_site.__doc__)
    add_site_arg(init_parser)
    init_parser.set_defaults(func=cmd_init_site)

    # fantail clean
    clean_parser = subparsers.add_parser('clean', description=cmd_clean_site.__doc__)
    clean_parser.add_argument('-y', dest='answer_yes', action='store_true',
                              help='Don\'t prompt for confirmation; assumes yes')
    add_site_arg(clean_parser)
    clean_parser.set_defaults(func=cmd_clean_site)

    # fantail build
    build_parser = subparsers.add_parser('build', description=cmd_build_site.__doc__)
    add_site_arg(build_parser)
    build_parser.set_defaults(func=cmd_build_site)

    # If no subcommand was given, print help and exit
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        exit(1)

    return args

def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(levelname)s: %(module)s: %(message)s')
    args.func(args)


if __name__ == '__main__':
    main()
