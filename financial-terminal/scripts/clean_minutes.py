"""Pure cleaning shared by daily and minute preparation; no I/O or fabricated bars."""
import numpy as np

def clean_minutes(frame):
    ordered=frame.sort_values('datetime',kind='stable')
    duplicates=int(ordered.datetime.duplicated().sum())
    unique=ordered.drop_duplicates('datetime',keep='last')
    valid=(unique.datetime.notna() & np.isfinite(unique[['Open','High','Low','Close','Volume']].to_numpy()).all(axis=1)
        & (unique[['Open','High','Low','Close']]>0).all(axis=1) & (unique.Volume>=0)
        & (unique.High>=unique[['Open','Close','Low']].max(axis=1))
        & (unique.Low<=unique[['Open','Close','High']].min(axis=1)))
    return unique[valid].copy(),duplicates,int((~valid).sum())
