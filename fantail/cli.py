import argparse

from staticsite import StaticSiteEnvironment

def parse_args():
    parser = argparse.ArgumentParser(description='fantail is a static site generator')
    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')
    subparsers.required = True

    # Common arguments
    parser.add_argument('-e', dest='env_dir', default='./',
                             help='Directory to use as the environment. Defaults to %(default)s')
    parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Switch on verbose logging')

    # fantail init
    init_parser = subparsers.add_parser('init', description='Create a new environment')

    # fantail clean
    clean_parser = subparsers.add_parser('clean', description='Cleans the environment')
    clean_parser.add_argument('-y', dest='answer_yes', action='store_true',
                              help='Don\'t prompt for confirmation; assumes yes')

    # fantail build
    build_parser = subparsers.add_parser('build', description='Builds the environment')

    return parser.parse_args()

def dispatch(args):
    _funcs = {'init': 'init_env',
              'clean': 'clean_env',
              'build': 'build_site'}
    func_name = _funcs.get(args.cmd, None)
    if func_name is None:
        print('Error: unknown function (bug?): ' + args.cmd)
        exit(1)

    site = StaticSiteEnvironment(args.env_dir, debug=args.debug)
    getattr(site, func_name)()

def main():
    args = parse_args()
    dispatch(args)


if __name__ == '__main__':
    main()
