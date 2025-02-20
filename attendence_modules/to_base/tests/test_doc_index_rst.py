import glob
import logging
import os

from docutils import io, nodes
from docutils.core import publish_programmatically

from odoo.tests import TransactionCase
from odoo.tools import config

from odoo.modules import module

from odoo.addons.base.models.ir_module import MyFilterMessages, MyWriter

_logger = logging.getLogger(__name__)


class TestDocRst(TransactionCase):

    def test_valid_doc_rst(self):
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
            for doc_rst in glob.glob(module.get_module_path(mod) + '/doc/*.rst'):
                if not os.path.isfile(doc_rst):
                    continue
                with open(doc_rst, 'r', encoding='utf-8') as f:
                    output, pub = publish_programmatically(
                        source_class=io.StringInput, source=f.read(), source_path=None,
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
                        msg = 'Warning at module %s.doc.%s\n' % (mod, doc_rst.split('/')[-1])
                        for node in node_messages:
                            msg += "docutils' system message present: %s\n" % str(node)
                            node.parent.remove(node)
                        _logger.warning(msg)

        MyFilterMessages.apply = _apply._original_method
