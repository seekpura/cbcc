from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.action_transports import materialize_transport_descriptors

materialize_transport_descriptors(ROOT / 'transport', server_url='/')
