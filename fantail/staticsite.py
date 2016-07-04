import email
import logging
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateNotFound
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory

from fantail import __version__
from fantail.git import GitRepository
from fantail.plugins.registry import load_plugins
from fantail.fileutils import *

class StaticSite(object):
    """
    This class represents a static site to be managed.
    """

    # Absolute path to this site, set in __init__
    path = None

    # GitReposity instance for the site. Will remain as None if git support
    # is disabled.
    git_repo = None

    # Absolute path to templates in the fantail package (not site)
    pkg_templates_path = os.path.join(os.path.dirname(__file__), 'templates')

    # Base template to use if no template: header is specified in a page
    base_template_name = 'base.html'

    # System context to add to each template
    _system_context = {'version': __version__}

    # Plugins registered by load_plugins()
    plugins = None

    def __init__(self, env_dir, git_support=True):
        # Absolute path of this environment
        self.path = os.path.abspath(env_dir)
        self.git_support = git_support

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
        except FileExistsError:
            logging.error('Site at {} already exists. Please remove it ' \
                          'before trying again.'.format(self.path))
            exit(2)
        if self.git_support:
            self.git_repo = GitRepository(self.path)
        logging.debug('Created site root at ' + self.path)

        # Create pages and templates
        os.makedirs(self.pages_dir)
        logging.debug('Created page directory at ' + self.pages_dir)
        shutil.copytree(self.pkg_templates_path, self.template_dir)
        logging.debug('Created template directory at ' + self.template_dir)

        g = ''
        if self.git_support:
            self.git_repo.git_add_all()
            self.git_repo.git_commit(msg='Initial fantail site')
            g = '(git)'
        logging.info('Created new site at {} {}'.format(self.path, g))

    def build_site(self):
        """
        Builds the site and writes output only if the build is successful.
        It is safe to call this over and over.
        """

        self.assert_site_exists()

        page_map = map_input_output_files(self.pages_dir)
        if len(page_map) == 0:
            logging.warning('No pages to generate from ' + self.pages_dir)
        else:
            logging.debug('Will generate the following pages from {0}: {1}'.format(
                self.pages_dir, str(page_map)))

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

    def _render_page(self, input_filename, output_filename):
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

        return template_name, page.items(), content

    def _render_static(self, input_filename, output_filename):
        with open(input_filename, 'r') as fp:
            return fp.read()

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
            if output_filename[0] == '/':
                output_filename = output_filename[1:]
            path = os.path.join(output_dir, output_filename)
            leading_dir = os.path.dirname(path)
            os.makedirs(leading_dir, exist_ok=True)

            if input_filename.endswith('.txt'):
                template_name, headers, output = self._render_page(input_filename, path)
            else:
                output = self._render_static(input_filename, path)
                template_name = None # no template, will render content only
                headers = {}

            # Gather context. The system context always takes precedence.
            # TODO: should it?
            context = dict(headers)
            context['content'] = output
            context.update(self._system_context)

            # Pass the entry through the template system and write output
            if template_name:
                try:
                    template = env.get_template(template_name)
                except TemplateNotFound as e:
                    logging.error('{0}: Template not found: {1}'.format(
                        input_filename, template_name
                    ))
                    exit(3)
            else:
                template = Template('{{ content }}')

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
            mirror_tree(temp_dir, self.output_dir, exclude=['.git'])

        p = subprocess.run(['tree', self.output_dir], check=True,
                       stdout=subprocess.PIPE)
        logging.info('Finished. Output directory: ' + p.stdout.decode('utf-8'))
