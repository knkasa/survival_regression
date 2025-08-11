from lifelines.datasets import load_rossi

# https://qiita.com/roki18d/items/b9aef6e3891e5b3a1f7b

rossi = load_rossi()
rossi.head()

from lifelines import CoxPHFitter
from lifelines.datasets import load_rossi

rossi = load_rossi()

cph = CoxPHFitter()
cph.fit(rossi, duration_col='week', event_col='arrest')

cph.print_summary()

