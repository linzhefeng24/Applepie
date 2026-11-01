import sys,unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from clean_minutes import clean_minutes
class MinuteCleaningTests(unittest.TestCase):
 def test_stable_deduplication_invalid_time_and_ohlc_do_not_mutate_input(self):
  data=pd.DataFrame(dict(datetime=pd.to_datetime(['2026-10-23 09:32','2026-10-23 09:30','2026-10-23 09:30','2026-10-23 09:31',None]),Open=[101,100,102,100,100],High=[103,101,103,90,101],Low=[99,99,101,99,99],Close=[102,100,102,100,100],Volume=[1,1,2,1,1]))
  original=data.copy(deep=True);result,duplicates,rejected=clean_minutes(data)
  pd.testing.assert_frame_equal(data,original)
  self.assertEqual(duplicates,1);self.assertEqual(rejected,2);self.assertEqual(len(result),2)
  self.assertEqual(result.iloc[0].Close,102);self.assertEqual(result.datetime.dt.strftime('%H:%M').tolist(),['09:30','09:32'])
