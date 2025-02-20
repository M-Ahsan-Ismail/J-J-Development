import ast

import logging
import os

from docutils import io, nodes
from docutils.core import publish_programmatically

from odoo.tests import TransactionCase
from odoo.tools import pycompat, config

from odoo.modules import module

from odoo.addons.base.models.ir_module import MyFilterMessages, MyWriter

_logger = logging.getLogger(__name__)


class TestManifestDescription(TransactionCase):

    def test_valid_manifest_description(self):
        # patch method to custom msg warning
        def _apply(self):
            pass
        _apply._original_method = MyFilterMessages.apply
        MyFilterMessages.apply = _apply

        settings_overrides = {
            'embed_stylesheet': False,
            'doctitle_xform': False,
            'output_encoding': 'unicode',
            'xml_declaration': False,
            'file_insertion_enabled': False,
            'report_level': 5,  # none
        }

        odoo_addons_path = os.path.join(os.path.dirname(config['root_path']), 'addons')
        modules = [mod for mod in module.get_modules() if odoo_addons_path not in os.path.dirname(module.get_module_path(mod))]
        for mod in modules:
            module_path = module.get_module_path(mod)
            manifest_path = module.module_manifest(module_path)
            if os.path.exists(manifest_path):
                with open(manifest_path, 'rb') as md:
                    manifest_data = md.read()

            manifest = ast.literal_eval(pycompat.to_text(manifest_data))
            for key in manifest.keys():
                if key.startswith('description'):
                    output, pub = publish_programmatically(
                        source_class=io.StringInput, source=manifest[key], source_path=None,
                        destination_class=io.StringOutput,
                        destination=None, destination_path=None,
                        reader=None, reader_name='standalone',
                        parser=None, parser_name='restructuredtext',
                        writer=MyWriter(), writer_name='pseudoxml',
                        settings=None, settings_spec=None,
                        settings_overrides=settings_overrides,
                        config_section=None,
                        enable_exit_status=False
                    )
                    node_messages = pub.document.traverse(nodes.system_message)
                    if node_messages:
                        msg = 'Warning at module %s.__manifest__.%s\n' % (mod, key)
                        for node in node_messages:
                            msg += "docutils' system message present: %s\n" % str(node)
                            node.parent.remove(node)
                        _logger.warning(msg)
                    # TODOs: may warn incorrectly if blockquote is used in manifest
                    if '<blockquote>' in output and '<blockquote>' not in manifest[key]:
                        msg = 'RST syntax error at module %s.__manifest__.%s\n' % (mod, key)
                        _logger.warning(msg)

        MyFilterMessages.apply = _apply._original_method
