import email
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import logging
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory

# Fix path for following package imports
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fantail import __version__

class StaticSiteEnvironment(object):
    """
    This class represents a static site environment. An environment
    contains directories for templates, pages and an output directory.
    Sensible defaults exist for treating the current working directory
    as an environment.
    """

    # Absolute path to this environment
    path = None

    # Base template to use if no template: header is specified in a page.
    base_template_name = 'base.html'

    # System context to add to each template
    _system_context = {'version': __version__}

    def __init__(self, env_dir, debug=False):
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(levelname)s: %(message)s')

        # Absolute path of this environment
        self.path = os.path.abspath(env_dir)
        logging.debug('Welcome from ' + repr(self))

    def __repr__(self):
        return '<StaticSiteEnvironment "{path}">'.format(path=self.path)

    @property
    def template_dir(self):
        return os.path.join(self.path, 'templates')

    @property
    def pages_dir(self):
        return os.path.join(self.path, 'pages')

    @property
    def output_dir(self):
        return os.path.join(self.path, 'output')

    def init_env(self):
        """
        Checks the environment to ensure it contains the required directories.
        Creates them if not. The output directory is left alone until the
        site is successfully generated to prevent any loss if the generation
        fails.
        """
        for reldir in [self.template_dir, self.pages_dir]:
            os.makedirs(reldir, exist_ok=True)
        print('Created new environment at ' + self.path)

    def build_site(self):
        page_map = self.map_pages()
        self.write_output(page_map)

    def clean_env(self):
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)
        print('Removed output directory from ' + self.path)

    def map_pages(self):
        """
        Creates a dictionary of input_file -> output_file of each page in the
        pages directory. The directory structure is maintained with each
        subpage being placed in its own directory and named index.html.

        For example:

        /pages
        * index.txt -> /output/index.html
        * /blog
           * hello-world.txt -> /output/blog/hello-world/index.html
           * how-to-use-fantail.txt -> /output/blog/how-to-use-fantail/index.html
        """

        output_pages = {}

        for root, dirs, files in os.walk(self.pages_dir):
            prefix = root.replace(self.pages_dir, '')
            for p in files:
                if p == 'index.txt':
                    output_filename = '/index.html'
                else:
                    title = os.path.splitext(p)[0]
                    output_filename = prefix + '/' + title + '/index.html'

                input_filename = os.path.join(root, p)
                output_pages[input_filename] = output_filename

        if len(output_pages) == 0:
            logging.warning('No pages to generate from ' + self.pages_dir)
        else:
            logging.debug('Will generate the following pages from {0}: {1}'.format(
                self.pages_dir, str(output_pages)))

        return output_pages

    def generate_pages(self, page_map, output_dir):
        """
        Takes a page map as returned by map_pages() and generates each page
        using the templates loaded with Jinja2.
        """

        loader = FileSystemLoader(self.template_dir)
        env = Environment(loader=loader)

        for input_filename, output_filename in page_map.items():
            # Join the full path name and create intermediate output dirs
            # We skip the first character of the output filename (which is /)
            # or os.path.join won't properly join the paths.
            path = os.path.join(output_dir, output_filename[1:])
            leading_dir = os.path.dirname(path)
            os.makedirs(leading_dir, exist_ok=True)

            # Parse the entry
            with open(input_filename, 'r') as fp:
                page = email.message_from_string(fp.read())
                post = page.get_payload()
            template_name = page.get('template', self.base_template_name)

            # Gather context. The system context always takes precedence.
            # TODO: should it?
            context = dict(page.items())
            context['content'] = post
            context.update(self._system_context)

            # Pass the entry through the template system and write output
            try:
                template = env.get_template(template_name)
            except TemplateNotFound as e:
                logging.error('{0}: Template not found: {1}'.format(
                    input_filename, template_name
                ))
                exit(3)
            with open(path, 'w') as fp:
                fp.write(template.render(context))
                fp.write(os.linesep)
            logging.debug('Wrote {0} from {1}'.format(path, input_filename))

    def write_output(self, page_map):
        """
        Generate the output pages to a temporary directory so not
        to trample over any existing pages if there is a failure.
        """
        with TemporaryDirectory() as temp_dir:
            self.generate_pages(page_map, temp_dir)
            # If we get here without an exception, the full site was generated
            # successfully, so move the output files over from the temporary
            shutil.rmtree(self.output_dir, ignore_errors=True)
            shutil.copytree(temp_dir, self.output_dir)

        p = subprocess.run(['tree', self.output_dir], check=True,
                       stdout=subprocess.PIPE)
        logging.info('Finished. Output directory: ' + p.stdout.decode('utf-8'))
