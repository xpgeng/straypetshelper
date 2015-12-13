import sae
sae.add_vendor_dir('vendor')

from main import app

application = sae.create_wsgi_app(app) 