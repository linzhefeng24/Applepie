import os
from transport.server import serve
from optimization.analysis import analyze
if __name__=='__main__':serve('quant_optimizer',os.environ.get('HTTP_PORT','8104'),'/analyze',analyze)
