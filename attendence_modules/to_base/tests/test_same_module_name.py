import os
from os.path import join as opj

import odoo
from odoo.modules import get_modules
from odoo.modules.module import MANIFEST_NAMES

from odoo.tests import TransactionCase


class TestSameModuleName(TransactionCase):

    def test_same_module_name(self):
        """Check the same module name between the addons"""
        modules_paths = {}
        for module_name in get_modules():
            module_paths = []
            for adp in odoo.addons.__path__:
                files = [opj(adp, module_name, manifest) for manifest in MANIFEST_NAMES] +\
                        [opj(adp, module_name + '.zip')]
                if any(os.path.exists(f) for f in files):
                    module_paths.append(adp)
            if len(module_paths) > 1:
                modules_paths[module_name] = module_paths

        if modules_paths:
            msg = ''
            for k, v in modules_paths.items():
                msg += 'Module "%s" is duplicated at the addons: "%s"\n' % (k, ', '.join(v))
            self.fail(msg)
