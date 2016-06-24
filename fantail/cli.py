import argparse

from staticsite import StaticSite

def parse_args():
    parser = argparse.ArgumentParser(description='fantail is a static site generator')
    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')
    subparsers.required = True

    def add_site_arg(this_parser):
        """
        Adds the common site argument to the parser given as an argument.
        """
        this_parser.add_argument('site_directory', default='./fantail-site/',
                                 nargs='?', help='Directory where the site ' \
                                 'stored. Defaults to %(default)s')

    # Common arguments
    parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Switch on verbose logging')

    # fantail init
    init_parser = subparsers.add_parser('init', description='Create a new site')
    add_site_arg(init_parser)

    # fantail clean
    clean_parser = subparsers.add_parser('clean', description='Removes the output directory from a site')
    clean_parser.add_argument('-y', dest='answer_yes', action='store_true',
                              help='Don\'t prompt for confirmation; assumes yes')
    add_site_arg(clean_parser)

    # fantail build
    build_parser = subparsers.add_parser('build', description='Builds the site')
    add_site_arg(build_parser)

    return parser.parse_args()

def dispatch(args):
    _funcs = {'init': 'init_site',
              'clean': 'clean_site',
              'build': 'build_site'}
    func_name = _funcs.get(args.cmd, None)
    if func_name is None:
        print('Error: unknown function (bug?): ' + args.cmd)
        exit(1)

    site = StaticSite(args.site_directory, debug=args.debug)
    getattr(site, func_name)()

def main():
    args = parse_args()
    dispatch(args)


if __name__ == '__main__':
    main()
