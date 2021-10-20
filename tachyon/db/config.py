from deta import Deta

from tachyon.settings import settings

client = Deta(settings.deta_key)
notes = client.AsyncBase(settings.notes_base)
