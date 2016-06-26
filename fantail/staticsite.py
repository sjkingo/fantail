import email
import logging
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory

from fantail import __version__
from fantail.plugins.registry import load_plugins

class StaticSite(object):
    """
    This class represents a static site to be managed.
    """

    # Absolute path to this site, set in __init__
    path = None

    # Absolute path to templates in the fantail package (not site)
    pkg_templates_path = os.path.join(os.path.dirname(__file__), 'templates')

    # Base template to use if no template: header is specified in a page
    base_template_name = 'base.html'

    # System context to add to each template
    _system_context = {'version': __version__}

    # Plugins registered by load_plugins()
    plugins = None

    def __init__(self, env_dir):
        # Absolute path of this environment
        self.path = os.path.abspath(env_dir)
        logging.debug('Welcome from ' + repr(self))

        self.plugins = load_plugins()

    def __repr__(self):
        return '<StaticSite "{path}">'.format(path=self.path)

    @property
    def template_dir(self):
        return os.path.join(self.path, 'templates')

    @property
    def pages_dir(self):
        return os.path.join(self.path, 'pages')

    @property
    def output_dir(self):
        return os.path.join(self.path, 'output')

    def assert_site_exists(self):
        if not os.path.isdir(self.path):
            logging.error('Site at ' + self.path + ' does not exist. '
                          'Please run `fantail init` first.')
            exit(2)

    def init_site(self):
        """
        Creates a new site by creating the required directories and populating
        templates from the packaged defaults. Will error out if the site
        directory already exists.

        The calling user must have permission to create directories at the
        path given.
        """

        try:
            os.makedirs(self.path) # site root
            logging.debug('Created site root at ' + self.path)
        except FileExistsError:
            logging.error('Site at {} already exists. Please remove it ' \
                          'before trying again.'.format(self.path))
            exit(2)

        # Create pages and templates
        os.makedirs(self.pages_dir)
        logging.debug('Created page directory at ' + self.pages_dir)
        shutil.copytree(self.pkg_templates_path, self.template_dir)
        logging.debug('Created template directory at ' + self.template_dir)

        # Create output directory
        os.makedirs(self.output_dir)
        logging.debug('Created output directory at ' + self.output_dir)

        print('Created new site at ' + self.path)

    def build_site(self):
        """
        Builds the site and writes output only if the build is successful.
        It is safe to call this over and over.
        """
        self.assert_site_exists()
        page_map = self._map_pages()
        self._write_output(page_map)

    def clean_site(self):
        """
        Cleans the site by removing the output directory only.
        Does not delete any pages or templates.
        """
        self.assert_site_exists()
        if os.path.isdir(self.output_dir):
            logging.info('Removed output directory from ' + self.path)
            shutil.rmtree(self.output_dir)
        else:
            logging.info('Nothing to do.')

    def _map_pages(self):
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

    def _generate_pages(self, page_map, output_dir):
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
                content = page.get_payload()
            template_name = page.get('template', self.base_template_name)

            # Apply filters to the content
            for filter in self.plugins.filters:
                filtered_content = filter(content)
                # Only update content if the filter returned something
                if filtered_content:
                    content = filtered_content
                else:
                    logging.warning('Filter `{}` did not return a value'.format(
                        filter.__name__
                    ))

            # Gather context. The system context always takes precedence.
            # TODO: should it?
            context = dict(page.items())
            context['content'] = content
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

    def _write_output(self, page_map):
        """
        Generate the output pages to a temporary directory so not
        to trample over any existing pages if there is a failure.
        """
        with TemporaryDirectory() as temp_dir:
            self._generate_pages(page_map, temp_dir)
            # If we get here without an exception, the full site was generated
            # successfully, so move the output files over from the temporary
            shutil.rmtree(self.output_dir, ignore_errors=True)
            shutil.copytree(temp_dir, self.output_dir)

        p = subprocess.run(['tree', self.output_dir], check=True,
                       stdout=subprocess.PIPE)
        logging.info('Finished. Output directory: ' + p.stdout.decode('utf-8'))
