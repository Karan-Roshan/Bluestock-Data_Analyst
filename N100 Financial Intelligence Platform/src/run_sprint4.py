"""Run Sprint 4 valuation generation and print dashboard launch instructions."""
from analytics.valuation import build_valuation

if __name__ == '__main__':
    print('=== Sprint 4 Valuation ===')
    out = build_valuation()
    print(f'valuation_summary.xlsx: {len(out)} companies')
    print(f"Flags: {out['flag'].value_counts().to_dict()}")
    print('\n=== Dashboard ===')
    print('Run: streamlit run src/dashboard/app.py')
