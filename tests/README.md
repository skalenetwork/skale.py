# Usage

Run full test pipeline:

- deploy fresh contracts (from `skale-manager`)
- copy `test.json` to skale-py/envs
- run `prepare_data.py`
- run `py.test`


Run test suite:
```bash
py.test
```

Run specific test:
```bash
py.test schains_test.py -k 'test_create_schain'
```

