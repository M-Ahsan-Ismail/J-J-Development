import os
import ast
from PIL import Image

from odoo.tests import TransactionCase
from odoo.tools import pycompat, config

from odoo.modules import module


class TestManifestImage(TransactionCase):

    def test_valid_manifest_images(self):
        odoo_addons_path = os.path.join(os.path.dirname(config['root_path']), 'addons')
        modules = [mod for mod in module.get_modules() if odoo_addons_path not in os.path.dirname(module.get_module_path(mod))]
        for mod in modules:
            module_path = module.get_module_path(mod)
            manifest_path = module.module_manifest(module_path)
            if os.path.exists(manifest_path):
                with open(manifest_path, 'rb') as md:
                    manifest_data = md.read()
            manifest = ast.literal_eval(pycompat.to_text(manifest_data))
            images = manifest.get('images', [])
            for image in images:
                if image:
                    abs_image_path = os.path.join(module_path, image)
                    exists_path = os.path.exists(abs_image_path)
                    with self.subTest(line=image):
                        self.assertTrue(exists_path, "This image path '%s' must be existed in module: %s" % (image, mod))
                        if exists_path:
                            Image.open(abs_image_path)
